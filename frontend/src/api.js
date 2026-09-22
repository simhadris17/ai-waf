const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Derive WebSocket base from API_BASE automatically:
// https://my-backend.onrender.com  →  wss://my-backend.onrender.com
// http://localhost:8000            →  ws://localhost:8000
function deriveWsBase() {
  const explicit = import.meta.env.VITE_WS_URL;
  if (explicit) return explicit;
  return API_BASE.replace(/^https:\/\//, "wss://").replace(/^http:\/\//, "ws://");
}

const WS_BASE = deriveWsBase();

function authHeaders() {
  const token = localStorage.getItem("waf_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handle(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const api = {
  /** Register a new user account. */
  register: (username, email, password) =>
    fetch(`${API_BASE}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password }),
    }).then(handle),

  /** Login and receive a JWT token. */
  login: (username, password) =>
    fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    }).then(handle),

  /** Get the current authenticated user's profile. */
  me: () =>
    fetch(`${API_BASE}/api/auth/me`, { headers: authHeaders() }).then(handle),

  getStats: () =>
    fetch(`${API_BASE}/api/logs/stats`, { headers: authHeaders() }).then(handle),

  getLogs: ({ limit = 50, label, search } = {}) => {
    const params = new URLSearchParams({ limit });
    if (label)  params.set("label",  label);
    if (search) params.set("search", search);
    return fetch(`${API_BASE}/api/logs?${params}`, { headers: authHeaders() }).then(handle);
  },

  simulate: (text) =>
    fetch(`${API_BASE}/api/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ text }),
    }).then(handle),

  /** Opens the live WebSocket with the JWT token for authentication.
   *  Automatically uses wss:// in production (https → wss). */
  liveSocket: () => {
    const token = localStorage.getItem("waf_token") || "";
    return new WebSocket(`${WS_BASE}/ws/live?token=${encodeURIComponent(token)}`);
  },
};
