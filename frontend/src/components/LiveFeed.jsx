import { useEffect, useRef } from "react";

export default function LiveFeed({ events }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  return (
    <div className="terminal" ref={scrollRef}>
      {events.length === 0 && (
        <div className="terminal-empty">Waiting for traffic… send a request to see it here.</div>
      )}
      {events.map((e, i) => (
        <div className="terminal-line" key={i}>
          <span className="terminal-time">{e.time}</span>
          <span className={`terminal-tag ${e.label}`}>{e.label}</span>
          <span className="terminal-path">
            {e.path} {e.blocked ? "· BLOCKED" : ""} ({e.confidence.toFixed(2)})
          </span>
        </div>
      ))}
    </div>
  );
}
