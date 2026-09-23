"""
Attack detector.

Loads the fine-tuned DistilBERT classifier from MODEL_DIR if it exists AND
if torch + transformers are installed. Falls back to a transparent keyword
heuristic otherwise — this lets the whole stack run on Render free tier
(no PyTorch) while still blocking obvious attack patterns.
"""
import html
import logging
import os
import re
from difflib import SequenceMatcher
from urllib.parse import unquote_plus
from urllib.parse import urlparse

import requests

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

_ATTACK_PATTERNS = tuple(re.compile(pattern, re.IGNORECASE) for pattern in (
    r"<\s*script\b",
    r"\bon(?:error|load|click)\s*=",
    r"\bjavascript\s*:",
    r"\bunion\s+(?:all\s+)?select\b",
    r"\b(?:select|insert|update|delete|drop)\s+.+\b(?:from|into|where|table)\b",
    r"(?:'|\")\s*(?:or|and)\s+[^\s]+\s*=\s*[^\s]+",
    r"\b(?:or|and)\s+\d+\s*=\s*\d+",
    r"\bsleep\s*\(\s*\d+",
    r"\b(?:xp_cmdshell|load_file|base64_decode|eval)\s*\(",
    r"(?:\.\./|\.\.\\)+",
    r"/(?:etc/(?:passwd|shadow)|windows/win\.ini|boot\.ini)\b",
    r"\b(?:cmd|exec|command)\s*=",
    r"\b(?:wget|curl|nc)\s+[^\s]+",
    r"\bwhoami\b",
    r"\brm\s+-rf\b",
    r"\{\{\s*\d+\s*[+*\-/]\s*\d+\s*\}\}",
))
_KNOWN_BRAND_DOMAINS = (
    "apple.com",
    "amazon.com",
    "facebook.com",
    "github.com",
    "google.com",
    "instagram.com",
    "linkedin.com",
    "microsoft.com",
    "paypal.com",
)


def _normalize(text: str) -> str:
    """Decode common URL/HTML obfuscation without changing normal URLs."""
    normalized = text
    for _ in range(3):
        decoded = unquote_plus(normalized)
        if decoded == normalized:
            break
        normalized = decoded
    return html.unescape(normalized).lower().replace("\x00", "")


def _looks_like_brand_typosquat(text: str) -> bool:
    candidate = text.strip()
    if not re.match(r"^[a-z][a-z0-9+.-]*://", candidate, re.IGNORECASE):
        return False

    hostname = (urlparse(candidate).hostname or "").lower().rstrip(".")
    if not hostname or hostname in _KNOWN_BRAND_DOMAINS:
        return False

    for brand in _KNOWN_BRAND_DOMAINS:
        if hostname.endswith(f".{brand}"):
            return False
        if SequenceMatcher(None, hostname, brand).ratio() >= 0.82:
            return True
    return False


def _safe_browsing_threat(text: str) -> bool | None:
    """Return True/False for a configured reputation result, or None if unavailable."""
    api_key = settings.GOOGLE_SAFE_BROWSING_API_KEY.strip()
    parsed = urlparse(text.strip())
    if not api_key or parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None

    endpoint = (
        "https://safebrowsing.googleapis.com/v4/threatMatches:find"
        f"?key={api_key}"
    )
    payload = {
        "client": {"clientId": "ai-waf", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION",
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": text.strip()}],
        },
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=3)
        response.raise_for_status()
    except requests.RequestException:
        logger.warning("Google Safe Browsing lookup failed", exc_info=True)
        return None

    return bool(response.json().get("matches"))


def _keyword_fallback(text: str) -> tuple[str, float]:
    normalized = _normalize(text)
    reputation_result = _safe_browsing_threat(normalized)
    if reputation_result is True:
        return "ATTACK", 0.99
    if _looks_like_brand_typosquat(normalized):
        return "ATTACK", 0.90
    if any(pattern.search(normalized) for pattern in _ATTACK_PATTERNS):
        return "ATTACK", 0.95
    if any(kw in normalized for kw in _ATTACK_KEYWORDS):
        return "ATTACK", 0.95
    return "SAFE", 0.10


class AttackDetector:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._torch = None
        self._load_model()

    def _load_model(self):
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
        """Returns (label, confidence, method)."""
        if not text:
            return "SAFE", 0.0, "none"

        # Deterministic checks always run first, independent of model confidence.
        kw_label, kw_conf = _keyword_fallback(text)
        if kw_label == "ATTACK":
            return kw_label, kw_conf, "keyword"

        if self.model is None:
            return "SAFE", 0.10, "none"

        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, padding=True, max_length=128
        )
        with self._torch.no_grad():
            outputs = self.model(**inputs)

        probs = self._torch.softmax(outputs.logits, dim=-1)[0]
        class_id = int(self._torch.argmax(probs).item())
        confidence = float(probs[class_id].item())
        configured_label = self.model.config.id2label.get(class_id, "")
        label = configured_label.upper()
        if label not in {"SAFE", "ATTACK"}:
            label = "ATTACK" if class_id == 1 else "SAFE"

        if label == "ATTACK" and confidence < settings.ATTACK_CONFIDENCE_THRESHOLD:
            return "SAFE", round(1 - confidence, 4), "none"

        return label, round(confidence, 4), "ml" if label == "ATTACK" else "none"


# Single shared instance, loaded once at process startup.
detector = AttackDetector()
