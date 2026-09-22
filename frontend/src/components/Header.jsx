export default function Header({ connected, onLogout }) {
  return (
    <div className="topbar">
      <div className="topbar-inner">
        <div className="brand">
          <span className="brand-mark" />
          AI-WAF · LIVE TRAFFIC CONSOLE
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span className="status-pill">
            <span className={`status-dot ${connected ? "live" : ""}`} />
            {connected ? "STREAM CONNECTED" : "RECONNECTING…"}
          </span>
          <button className="logout-btn" onClick={onLogout}>
            Log out
          </button>
        </div>
      </div>
    </div>
  );
}
