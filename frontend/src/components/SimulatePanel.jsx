import { useState } from "react";
import { api } from "../api";

export default function SimulatePanel({ onScanComplete }) {
  const [text, setText]     = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState("");

  async function handleScan(e) {
    e.preventDefault();
    if (!text.trim()) return;
    setResult(null);
    setError("");
    setLoading(true);
    try {
      const data = await api.simulate(text);
      setResult(data);
      onScanComplete?.();
    } catch (err) {
      setError(err.message || "Scan failed");
    } finally {
      setLoading(false);
    }
  }

  const isAttack = result?.label === "ATTACK";

  return (
    <div className="simulate-panel">
      <div className="simulate-label">Payload Scanner</div>

      <form onSubmit={handleScan} className="simulate-input-row">
        <input
          className="simulate-input"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter a URL path or payload to scan…  e.g.  /search?q=' OR 1=1--"
          spellCheck={false}
        />
        <button className="btn-primary" disabled={loading || !text.trim()}>
          {loading ? "Scanning…" : "🔍 Scan"}
        </button>
      </form>

      {error && (
        <div className="login-error" style={{ marginTop: 12 }}>{error}</div>
      )}

      {result && (
        <div className={`simulate-result ${result.label}`}>
          <div className="result-header">
            <span style={{ fontSize: 20 }}>{isAttack ? "🚨" : "✅"}</span>
            <span className="result-label">
              {isAttack ? "ATTACK DETECTED" : "SAFE"}
            </span>
            {result.attack_type && (
              <span className={`result-tag ${result.attack_type}`}>
                {result.attack_type === "ml" ? "🧠 ML Model" : "🔑 Keyword"}
              </span>
            )}
          </div>
          <div className="result-meta">
            <span>Confidence: <strong style={{ color: "var(--text-primary)" }}>
              {(result.confidence * 100).toFixed(1)}%
            </strong></span>
            <span>Payload: <strong style={{ color: "var(--text-primary)", fontFamily: "var(--font-mono)" }}>
              {result.text.slice(0, 80)}{result.text.length > 80 ? "…" : ""}
            </strong></span>
          </div>
        </div>
      )}
    </div>
  );
}
