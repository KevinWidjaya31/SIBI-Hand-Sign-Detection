import { useEffect, useRef } from "react"

/**
 * HistoryLog – shows recent detected gestures in a fixed-size,
 * scrollable container so the page layout never shifts.
 *
 * Props:
 *  - history: Array of { id, letter, time }
 *  - onClear: callback to clear history
 */
export default function HistoryLog({ history, onClear }) {
  const listRef = useRef(null)

  // Auto-scroll to top when a new item is added
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTo({ top: 0, behavior: "smooth" })
    }
  }, [history.length])

  return (
    <div className="history-log" id="history-log">
      <div className="history-header">
        <div className="section-label">Detection History</div>
        {history.length > 0 && (
          <button
            className="history-clear-btn"
            id="clear-history-btn"
            onClick={onClear}
            title="Clear history"
            aria-label="Clear history"
          >
            {/* Trash icon */}
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="3 6 5 6 21 6" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
            </svg>
          </button>
        )}
      </div>

      <div className="history-card" id="history-card">
        {history.length === 0 ? (
          <div className="history-empty">No detections yet</div>
        ) : (
          <div className="history-list" ref={listRef}>
            {history.map((item, i) => (
              <div
                key={item.id}
                className="history-item"
                style={{ animationDelay: `${i * 0.03}s` }}
              >
                <span className="history-letter">{item.letter}</span>
                <span className="history-time">{item.time}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
