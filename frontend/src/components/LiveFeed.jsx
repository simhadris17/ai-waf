import { useEffect, useRef } from "react";

export default function LiveFeed({ events }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">
          <span className="panel-title-dot" />
          Live Traffic
        </span>
        <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
          {events.length} events
        </span>
      </div>

      <div className="live-feed">
        {events.length === 0 ? (
          <div className="feed-empty">
            <div className="feed-empty-icon">📡</div>
            <span>Waiting for traffic…</span>
          </div>
        ) : (
          events.slice().reverse().map((ev, i) => (
            <div key={i} className={`feed-line ${ev.label}`}>
              <span className="feed-time">{ev.time}</span>
              <span className={`feed-badge ${ev.label}`}>{ev.label}</span>
              <span className="feed-path">{ev.path}</span>
              <span className="feed-conf">{(ev.confidence * 100).toFixed(0)}%</span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
