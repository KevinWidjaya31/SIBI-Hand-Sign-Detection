export default function ResultPanel({ letter, confidence, status, top3, stability, fps, latency }) {
  return (
    <div className="result-panel">
      <div className="section-label">Detection Result</div>
      <div className="result-card" id="result-card">
        {/* Status Indicator */}
        <div className={`status-indicator status-${status.type}`} id="status-indicator">
          <span className="status-dot" />
          <span className="status-text">{status.text}</span>
        </div>

        {/* Detected Letter */}
        <div className="detected-letter" id="detected-letter" key={letter}>
          {letter}
        </div>

        {/* Confidence Bar */}
        <div className="confidence-block" id="confidence-block">
          <div className="confidence-header">
            <span className="confidence-label">Confidence</span>
            <span className="confidence-value">{confidence.toFixed(1)}%</span>
          </div>
          <div className="progress-track">
            <div
              className="progress-fill"
              style={{ width: `${Math.min(confidence, 100)}%` }}
            />
          </div>
        </div>

        {/* Top 3 Predictions */}
        {top3 && top3.length > 0 && (
          <div className="top3-block" id="top3-block">
            <div className="top3-label">Top Predictions</div>
            <div className="top3-list">
              {top3.map((item, i) => (
                <div key={i} className={`top3-item ${i === 0 ? "top3-first" : ""}`}>
                  <span className="top3-letter">{item.letter}</span>
                  <div className="top3-bar-track">
                    <div
                      className="top3-bar-fill"
                      style={{ width: `${Math.min(item.confidence, 100)}%` }}
                    />
                  </div>
                  <span className="top3-pct">{item.confidence.toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Stability Indicator */}
        <div className={`stability-badge ${stability === "Stable" ? "stable" : "unstable"}`} id="stability-badge">
          <span className="stability-dot" />
          {stability}
        </div>

        {/* Real-Time Performance */}
        <div className="perf-stats" id="perf-stats">
          <div className="perf-item">
            <span className="perf-label">FPS</span>
            <span className="perf-value">{fps}</span>
          </div>
          <div className="perf-divider" />
          <div className="perf-item">
            <span className="perf-label">Latency</span>
            <span className="perf-value">{latency}ms</span>
          </div>
          <div className="perf-divider" />
          <div className="perf-item">
            <span className="perf-label">Status</span>
            <span className="perf-value">{stability}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
