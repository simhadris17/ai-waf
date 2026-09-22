import { useEffect, useRef, useState } from "react";

function AnimatedNumber({ value, decimals = 0 }) {
  const [display, setDisplay] = useState(0);
  const ref = useRef(null);

  useEffect(() => {
    if (value === null || value === undefined) return;
    const target = parseFloat(value);
    const start = display;
    const duration = 800;
    const startTime = performance.now();

    function step(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setDisplay(start + (target - start) * eased);
      if (progress < 1) ref.current = requestAnimationFrame(step);
    }

    ref.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(ref.current);
  }, [value]); // eslint-disable-line

  if (value === null || value === undefined) return <span>—</span>;
  return <span>{decimals ? display.toFixed(decimals) : Math.round(display).toLocaleString()}</span>;
}

export default function StatCards({ stats }) {
  const cards = [
    {
      key: "total", icon: "📊", label: "Total Requests",
      value: stats?.total, sub: "All time", decimals: 0,
    },
    {
      key: "safe", icon: "✅", label: "Safe",
      value: stats?.safe, sub: "Allowed through", decimals: 0,
    },
    {
      key: "attack", icon: "⚠️", label: "Attacks",
      value: stats?.attack, sub: "Threats detected", decimals: 0,
    },
    {
      key: "blocked", icon: "🚫", label: "Blocked",
      value: stats?.blocked, sub: "Requests stopped", decimals: 0,
    },
    {
      key: "conf", icon: "🧠", label: "Avg Confidence",
      value: stats ? stats.avg_confidence * 100 : null,
      sub: "ML accuracy", decimals: 1, suffix: "%",
    },
  ];

  return (
    <div className="stat-grid">
      {cards.map(({ key, icon, label, value, sub, decimals, suffix }) => (
        <div key={key} className={`stat-card ${key}`}>
          <div className="stat-icon">{icon}</div>
          <div className="stat-label">{label}</div>
          <div className="stat-value">
            <AnimatedNumber value={value} decimals={decimals} />
            {suffix && value !== null && value !== undefined ? suffix : ""}
          </div>
          <div className="stat-sub">{sub}</div>
        </div>
      ))}
    </div>
  );
}
