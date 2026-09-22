import { useState } from "react";
import { api } from "../api";

export default function SimulatePanel() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleTest() {
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await api.simulate(text);
      setResult(res);
    } catch (err) {
      setResult({ label: "ERROR", confidence: 0, text: err.message, attack_type: null });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel">
      <div className="stat-label" style={{ marginBottom: 10 }}>
        Test a payload against the model
      </div>
      <div className="simulate-row">
        <input
          className="simulate-input"
          placeholder="e.g. admin' OR 1=1 --"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleTest()}
        />
        <button className="btn-primary" onClick={handleTest} disabled={loading}>
          {loading ? "Scanning…" : "Scan"}
        </button>
      </div>
      {result && (
        <div className={`result-badge ${result.label}`}>
          <span>{result.label}</span>
          <span style={{ opacity: 0.7 }}>·</span>
          <span>confidence {Number(result.confidence).toFixed(2)}</span>
          {result.attack_type && (
            <>
              <span style={{ opacity: 0.7 }}>·</span>
              <span className="attack-method-tag">via {result.attack_type}</span>
            </>
          )}
        </div>
      )}
    </div>
  );
}
