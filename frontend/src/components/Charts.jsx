import { useMemo } from "react";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from "recharts";

const COLORS = {
  SAFE:   "#00ff88",
  ATTACK: "#ff3366",
};

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "rgba(6,13,31,0.95)",
      border: "1px solid rgba(99,179,237,0.15)",
      borderRadius: 8,
      padding: "8px 12px",
      fontSize: 12,
      color: "#e8f4ff",
    }}>
      <strong>{payload[0].name}</strong>: {payload[0].value.toLocaleString()}
    </div>
  );
};

export default function Charts({ stats, events }) {
  const pieData = useMemo(() => {
    if (!stats) return [];
    return [
      { name: "Safe",   value: stats.safe },
      { name: "Attack", value: stats.attack },
    ].filter(d => d.value > 0);
  }, [stats]);

  const barData = useMemo(() => {
    const buckets = {};
    events.forEach(ev => {
      const key = ev.time?.slice(0, 5) || "??:??";
      if (!buckets[key]) buckets[key] = { time: key, ATTACK: 0, SAFE: 0 };
      buckets[key][ev.label] = (buckets[key][ev.label] || 0) + 1;
    });
    return Object.values(buckets).slice(-8);
  }, [events]);

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">
          <span className="panel-title-dot" style={{ background: "var(--purple)" }} />
          Analytics
        </span>
      </div>

      <div className="charts-inner">
        {/* Pie */}
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <ResponsiveContainer width="50%" height="100%">
            <PieChart>
              <Pie
                data={pieData.length ? pieData : [{ name: "No data", value: 1 }]}
                cx="50%" cy="50%"
                innerRadius="45%" outerRadius="75%"
                paddingAngle={3}
                dataKey="value"
                strokeWidth={0}
              >
                {pieData.length
                  ? pieData.map((entry) => (
                    <Cell key={entry.name} fill={COLORS[entry.name] || "#4a6080"} />
                  ))
                  : <Cell fill="#1e2d4a" />
                }
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>

          <div style={{ fontSize: 12, lineHeight: 2 }}>
            {pieData.map(d => (
              <div key={d.name} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{
                  width: 10, height: 10, borderRadius: 2,
                  background: COLORS[d.name], display: "inline-block",
                }} />
                <span style={{ color: "var(--text-muted)" }}>{d.name}</span>
                <span style={{ color: "var(--text-primary)", fontWeight: 700, fontFamily: "var(--font-mono)" }}>
                  {d.value.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Bar */}
        <div>
          <div style={{ fontSize: 10, color: "var(--text-muted)", marginBottom: 4, fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase" }}>
            Requests / minute
          </div>
          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={barData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(99,179,237,0.08)" />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#4a6080" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: "#4a6080" }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="SAFE"   fill="#00ff88" opacity={0.8} radius={[3,3,0,0]} />
              <Bar dataKey="ATTACK" fill="#ff3366" opacity={0.8} radius={[3,3,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
