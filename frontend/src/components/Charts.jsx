import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from "recharts";

const COLORS = { SAFE: "#2dd4a7", ATTACK: "#ff5470" };

/**
 * Bucket the last N events into 1-minute (or coarser) slots for the bar chart.
 */
function buildTimeSeries(events) {
  if (!events || events.length === 0) return [];
  const buckets = {};
  events.forEach((e) => {
    // e.time is a locale time string like "12:34:56"; bucket by minute
    const minute = e.time ? e.time.slice(0, 5) : "??:??";
    if (!buckets[minute]) buckets[minute] = { time: minute, SAFE: 0, ATTACK: 0 };
    buckets[minute][e.label] = (buckets[minute][e.label] || 0) + 1;
  });
  return Object.values(buckets).slice(-10); // last 10 minutes max
}

export default function Charts({ stats, events }) {
  const pieData = [
    { name: "SAFE",   value: stats?.safe   ?? 0 },
    { name: "ATTACK", value: stats?.attack ?? 0 },
  ];

  const hasData = (stats?.safe ?? 0) + (stats?.attack ?? 0) > 0;
  const timeSeries = buildTimeSeries(events);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Pie chart — overall traffic distribution */}
      <div className="panel" style={{ height: 280 }}>
        <div className="stat-label" style={{ marginBottom: 8 }}>
          Traffic distribution
        </div>
        {hasData ? (
          <ResponsiveContainer width="100%" height="86%">
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={4}
              >
                {pieData.map((d) => (
                  <Cell key={d.name} fill={COLORS[d.name]} stroke="none" />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: "#161f38",
                  border: "1px solid #23304f",
                  borderRadius: 8,
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: 12,
                }}
              />
              <Legend wrapperStyle={{ fontSize: 12, fontFamily: "Inter, sans-serif" }} />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="terminal-empty">No data yet.</div>
        )}
      </div>

      {/* Bar chart — requests by minute (live events) */}
      <div className="panel" style={{ height: 220 }}>
        <div className="stat-label" style={{ marginBottom: 8 }}>
          Requests per minute (live)
        </div>
        {timeSeries.length > 0 ? (
          <ResponsiveContainer width="100%" height="80%">
            <BarChart data={timeSeries} barSize={14}>
              <CartesianGrid strokeDasharray="3 3" stroke="#23304f" vertical={false} />
              <XAxis
                dataKey="time"
                tick={{ fill: "#7c89a8", fontSize: 11, fontFamily: "JetBrains Mono, monospace" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                allowDecimals={false}
                tick={{ fill: "#7c89a8", fontSize: 11, fontFamily: "JetBrains Mono, monospace" }}
                axisLine={false}
                tickLine={false}
                width={28}
              />
              <Tooltip
                contentStyle={{
                  background: "#161f38",
                  border: "1px solid #23304f",
                  borderRadius: 8,
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: 12,
                }}
              />
              <Bar dataKey="SAFE"   fill="#2dd4a7" radius={[3, 3, 0, 0]} />
              <Bar dataKey="ATTACK" fill="#ff5470" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="terminal-empty">Waiting for live traffic…</div>
        )}
      </div>
    </div>
  );
}
