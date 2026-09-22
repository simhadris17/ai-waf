import { useCallback, useEffect, useRef, useState } from "react";
import Header from "./components/Header";
import Login from "./components/Login";
import StatCards from "./components/StatCards";
import LiveFeed from "./components/LiveFeed";
import Charts from "./components/Charts";
import SimulatePanel from "./components/SimulatePanel";
import LogsTable from "./components/LogsTable";
import { api } from "./api";

export default function App() {
  const [authed, setAuthed] = useState(!!localStorage.getItem("waf_token"));
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const wsRef = useRef(null);

  const loadStats = useCallback(() => {
    api.getStats().then(setStats).catch(() => {});
  }, []);

  useEffect(() => {
    if (!authed) return;

    loadStats();
    const statsInterval = setInterval(loadStats, 5000);

    let socket;
    let retryTimer;

    function connect() {
      socket = api.liveSocket();
      wsRef.current = socket;

      socket.onopen = () => setConnected(true);
      socket.onclose = () => {
        setConnected(false);
        retryTimer = setTimeout(connect, 2000);
      };
      socket.onerror = () => socket.close();
      socket.onmessage = (msg) => {
        const data = JSON.parse(msg.data);
        setEvents((prev) => [
          ...prev.slice(-99),
          { ...data, time: new Date().toLocaleTimeString() },
        ]);
        setRefreshKey((k) => k + 1);
      };
    }

    connect();

    return () => {
      clearInterval(statsInterval);
      clearTimeout(retryTimer);
      socket && socket.close();
    };
  }, [authed, loadStats]);

  function handleLogout() {
    localStorage.removeItem("waf_token");
    setAuthed(false);
    wsRef.current?.close();
  }

  if (!authed) {
    return <Login onLoggedIn={() => setAuthed(true)} />;
  }

  return (
    <div className="app-shell">
      <Header connected={connected} onLogout={handleLogout} />

      <div className="main container">
        <StatCards stats={stats} />

        <div className="section-title">Live traffic</div>
        <div className="two-col">
          <LiveFeed events={events} />
          {/* Pass events so Charts can render the per-minute bar chart */}
          <Charts stats={stats} events={events} />
        </div>

        <div className="section-title">Payload scanner</div>
        <SimulatePanel />

        <div className="section-title">Request log</div>
        <LogsTable refreshKey={refreshKey} />
      </div>
    </div>
  );
}
