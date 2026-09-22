import { useState } from "react";
import { api } from "../api";

export default function Login({ onLoggedIn }) {
  const [mode, setMode]         = useState("login");
  const [username, setUsername] = useState("");
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]       = useState("");
  const [loading, setLoading]   = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await api.register(username, email, password);
      }
      const { access_token } = await api.login(username, password);
      localStorage.setItem("waf_token", access_token);
      onLoggedIn();
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function toggle() {
    setMode(m => m === "login" ? "register" : "login");
    setError("");
    setEmail("");
  }

  return (
    <div className="login-screen">
      {/* Animated background orbs */}
      <div className="login-bg-anim">
        <div className="login-orb" />
        <div className="login-orb" />
        <div className="login-orb" />
      </div>

      <form className="login-card" onSubmit={handleSubmit}>
        <div className="login-logo">
          <div className="login-logo-icon">🛡️</div>
        </div>

        <div className="login-title">AI-WAF</div>
        <div className="login-sub">
          {mode === "login"
            ? "Security Operations Dashboard"
            : "Create your account"}
        </div>

        {error && <div className="login-error">⚠️ {error}</div>}

        <div className="login-field">
          <label>Username</label>
          <input
            value={username}
            onChange={e => setUsername(e.target.value)}
            autoComplete="username"
            placeholder="Enter username"
            minLength={3}
            required
          />
        </div>

        {mode === "register" && (
          <div className="login-field">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              autoComplete="email"
              placeholder="you@example.com"
              required
            />
          </div>
        )}

        <div className="login-field">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            autoComplete={mode === "register" ? "new-password" : "current-password"}
            placeholder={mode === "register" ? "Min 8 characters" : "Enter password"}
            minLength={8}
            required
          />
        </div>

        <button className="btn-primary login-submit" disabled={loading}>
          {loading
            ? (mode === "login" ? "Authenticating…" : "Creating account…")
            : (mode === "login" ? "🔓 Sign In" : "🚀 Create Account")}
        </button>

        <div className="login-toggle">
          {mode === "login" ? (
            <>No account?{" "}
              <button type="button" className="link-btn" onClick={toggle}>Register</button>
            </>
          ) : (
            <>Already registered?{" "}
              <button type="button" className="link-btn" onClick={toggle}>Sign In</button>
            </>
          )}
        </div>
      </form>
    </div>
  );
}
