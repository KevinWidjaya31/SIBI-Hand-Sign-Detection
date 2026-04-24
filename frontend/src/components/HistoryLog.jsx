export default function HistoryLog({ history }) {
  return (
    <div className="history-log" id="history-log">
      <div className="section-label">Detection History</div>
      <div className="history-card">
        {history.length === 0 ? (
          <div className="history-empty">No detections yet</div>
        ) : (
          <div className="history-list">
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
