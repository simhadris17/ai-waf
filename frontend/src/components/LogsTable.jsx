import { useEffect, useState, useCallback } from "react";
import { api } from "../api";

export default function LogsTable({ refreshKey }) {
  const [logs, setLogs] = useState([]);
  const [label, setLabel] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    api
      .getLogs({ limit: 50, label: label || undefined, search: search || undefined })
      .then(setLogs)
      .catch(() => setLogs([]))
      .finally(() => setLoading(false));
  }, [label, search]);

  useEffect(() => {
    load();
  }, [load, refreshKey]);

  return (
    <div className="panel">
      <div className="filters">
        <select value={label} onChange={(e) => setLabel(e.target.value)}>
          <option value="">All labels</option>
          <option value="SAFE">SAFE</option>
          <option value="ATTACK">ATTACK</option>
        </select>
        <input
          placeholder="Search path…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button className="logout-btn" onClick={load}>
          {loading ? "Loading…" : "Refresh"}
        </button>
      </div>

      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>IP</th>
            <th>Method</th>
            <th>Label</th>
            <th>Confidence</th>
            <th>Blocked</th>
            <th>Path</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((l) => (
            <tr key={l.id}>
              <td>{new Date(l.created_at).toLocaleTimeString()}</td>
              <td style={{ color: "var(--text-muted)" }}>{l.client_ip ?? "—"}</td>
              <td>
                <span className="method-tag">{l.method ?? "—"}</span>
              </td>
              <td>
                <span className={`tag ${l.label}`}>{l.label}</span>
              </td>
              <td>{l.confidence.toFixed(2)}</td>
              <td style={{ color: l.blocked ? "var(--attack)" : "var(--text-muted)" }}>
                {l.blocked ? "Yes" : "No"}
              </td>
              <td>{l.path}</td>
            </tr>
          ))}
          {logs.length === 0 && (
            <tr>
              <td colSpan={7} style={{ color: "var(--text-muted)", fontFamily: "Inter" }}>
                No logs match the current filters.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
