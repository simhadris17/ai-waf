import { useEffect, useState } from "react";
import { api } from "../api";

const fmt = (dt) =>
  dt ? new Date(dt).toLocaleString("en-IN", { hour12: false, timeStyle: "short", dateStyle: "short" }) : "—";

export default function LogsTable({ refreshKey }) {
  const [logs, setLogs]   = useState([]);
  const [label, setLabel] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.getLogs({ limit: 100, label: label || undefined, search: search || undefined })
      .then(setLogs)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [refreshKey, label, search]);

  return (
    <div className="logs-panel">
      <div className="logs-toolbar">
        <input
          className="logs-search"
          placeholder="🔍  Search paths…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="logs-filter"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
        >
          <option value="">All</option>
          <option value="ATTACK">⚠️ Attack</option>
          <option value="SAFE">✅ Safe</option>
        </select>
        {loading && (
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Loading…</span>
        )}
        <span style={{ fontSize: 11, color: "var(--text-muted)", marginLeft: "auto" }}>
          {logs.length} rows
        </span>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>IP</th>
              <th>Method</th>
              <th>Path</th>
              <th>Label</th>
              <th>Conf</th>
              <th>Blocked</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: "center", padding: "32px", color: "var(--text-muted)" }}>
                  No records found
                </td>
              </tr>
            ) : logs.map((log) => (
              <tr key={log.id}>
                <td style={{ color: "var(--text-muted)", fontSize: 11 }}>{fmt(log.created_at)}</td>
                <td>{log.client_ip || "—"}</td>
                <td>
                  <span className={`method-tag ${log.method || ""}`}>
                    {log.method || "—"}
                  </span>
                </td>
                <td style={{ maxWidth: 260, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {log.path}
                </td>
                <td><span className={`tag ${log.label}`}>{log.label}</span></td>
                <td style={{ color: "var(--text-muted)" }}>
                  {(log.confidence * 100).toFixed(0)}%
                </td>
                <td>
                  <span className={`blocked-dot ${log.blocked ? "yes" : "no"}`} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
