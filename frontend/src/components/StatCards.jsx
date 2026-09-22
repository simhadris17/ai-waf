export default function StatCards({ stats }) {
  const cards = [
    { label: "Total requests", value: stats?.total ?? "—", cls: "" },
    { label: "Safe",           value: stats?.safe  ?? "—", cls: "safe" },
    { label: "Attacks detected", value: stats?.attack   ?? "—", cls: "attack" },
    { label: "Blocked",        value: stats?.blocked ?? "—", cls: "blocked" },
    { label: "Avg. confidence", value: stats ? stats.avg_confidence.toFixed(2) : "—", cls: "brand" },
  ];

  return (
    <div className="stat-grid">
      {cards.map((c) => (
        <div className="stat-card" key={c.label}>
          <div className="stat-label">{c.label}</div>
          <div className={`stat-value ${c.cls}`}>{c.value}</div>
        </div>
      ))}
    </div>
  );
}
