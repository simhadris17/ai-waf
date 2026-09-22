export default function Header({ connected, onLogout }) {
  return (
    <header className="header">
      <div className="header-logo">
        <div className="logo-icon">🛡️</div>
        <span className="logo-text">AI-WAF</span>
        <span className="logo-badge">Enterprise</span>
      </div>

      <div className="header-right">
        <div className={`status-pill ${connected ? "live" : "offline"}`}>
          <span className="status-dot" />
          {connected ? "Live" : "Offline"}
        </div>
        <button className="btn-ghost" onClick={onLogout}>Sign out</button>
      </div>
    </header>
  );
}
