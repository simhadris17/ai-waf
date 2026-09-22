"""
Attack detector.

Loads the fine-tuned DistilBERT classifier from MODEL_DIR if it exists AND
if torch + transformers are installed. Falls back to a transparent keyword
heuristic otherwise — this lets the whole stack run on Render free tier
(no PyTorch) while still blocking obvious attack patterns.
"""
import logging
import os

from app.config import get_settings

logger = logging.getLogger("ai-waf.detector")
settings = get_settings()

_ATTACK_KEYWORDS = [
    "<script", "onerror=", "onload=", "javascript:", "document.cookie",
    "' or 1=1", '" or 1=1', "' or 'a'='a", "union select", "drop table",
    "insert into", "delete from", "sleep(", "xp_cmdshell", "load_file",
    "../", "..\\", "/etc/passwd", "/etc/shadow", "boot.ini",
    "cmd=", "wget ", "curl ", "nc -e", "eval(", "base64_decode",
]


def _keyword_fallback(text: str) -> tuple[str, float]:
    lowered = text.lower()
    for kw in _ATTACK_KEYWORDS:
        if kw in lowered:
            return "ATTACK", 0.95
    return "SAFE", 0.10


class AttackDetector:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._torch = None
        self._load_model()

    def _load_model(self):
        # Check if the ML deps are even installed before attempting to load
        try:
            import torch  # noqa: F401
            import transformers  # noqa: F401
        except ImportError:
            logger.warning(
                "torch/transformers not installed - using keyword fallback. "
                "Install requirements.txt (full) to enable ML detection."
            )
            return

        if not os.path.isdir(settings.MODEL_DIR):
            logger.warning(
                "No trained model found at %s - using keyword fallback. "
                "Run `python -m app.ml.train` to train the real classifier.",
                settings.MODEL_DIR,
            )
            return

        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSequenceClassification

            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.MODEL_DIR, local_files_only=True
            )
            self.model = AutoModelForSequenceClassification.from_pretrained(
                settings.MODEL_DIR, local_files_only=True
            )
            self.model.eval()
            self._torch = torch
            logger.info("Loaded trained WAF model from %s", settings.MODEL_DIR)
        except Exception:
            logger.exception("Failed to load trained model, using keyword fallback")
            self.model = None

    def predict(self, text: str) -> tuple[str, float, str]:
        """Returns (label, confidence, method).

        label  - 'SAFE' or 'ATTACK'
        confidence - float 0–1
        method - 'none' | 'keyword' | 'ml'  — which detection path fired
        """
        if not text:
            return "SAFE", 0.0, "none"

        if self.model is None:
            kw_label, kw_conf = _keyword_fallback(text)
            method = "keyword" if kw_label == "ATTACK" else "none"
            return kw_label, kw_conf, method

        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, padding=True, max_length=128
        )
        with self._torch.no_grad():
            outputs = self.model(**inputs)

        probs = self._torch.softmax(outputs.logits, dim=-1)[0]
        class_id = int(self._torch.argmax(probs).item())
        confidence = float(probs[class_id].item())
        label = self.model.config.id2label[class_id]

        # Belt-and-braces: keyword hits always count as ATTACK even if the
        # model is unsure, since these are unambiguous, high-signal payloads.
        kw_label, kw_conf = _keyword_fallback(text)
        if kw_label == "ATTACK" and confidence < settings.ATTACK_CONFIDENCE_THRESHOLD:
            return kw_label, kw_conf, "keyword"

        method = "ml" if label == "ATTACK" else "none"
        return label, round(confidence, 4), method


# Single shared instance, loaded once at process startup.
detector = AttackDetector()
