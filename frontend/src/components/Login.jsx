import { useState } from "react";
import { api } from "../api";

export default function Login({ onLoggedIn }) {
  const [mode, setMode]         = useState("login");   // "login" | "register"
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
        // Auto-login after successful registration
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

  function toggleMode() {
    setMode((m) => (m === "login" ? "register" : "login"));
    setError("");
    setEmail("");
  }

  return (
    <div className="login-screen">
      <form className="login-card" onSubmit={handleSubmit}>
        <div className="login-title">AI-WAF Console</div>
        <div className="login-sub">
          {mode === "login"
            ? "Sign in to view live traffic and threat logs."
            : "Create an account to access the dashboard."}
        </div>

        {error && <div className="login-error">{error}</div>}

        <div className="login-field">
          <label htmlFor="username">Username</label>
          <input
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            minLength={3}
            required
          />
        </div>

        {mode === "register" && (
          <div className="login-field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
          </div>
        )}

        <div className="login-field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={mode === "register" ? "new-password" : "current-password"}
            minLength={8}
            required
          />
        </div>

        <button className="btn-primary login-submit" disabled={loading}>
          {loading ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
        </button>

        <div className="login-toggle">
          {mode === "login" ? (
            <>No account?{" "}
              <button type="button" className="link-btn" onClick={toggleMode}>
                Register
              </button>
            </>
          ) : (
            <>Already have an account?{" "}
              <button type="button" className="link-btn" onClick={toggleMode}>
                Sign in
              </button>
            </>
          )}
        </div>
      </form>
    </div>
  );
}
