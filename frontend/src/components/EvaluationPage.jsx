import { useState, useCallback } from "react"

export default function EvaluationPage() {
  const [loading, setLoading] = useState(false)
  const [evalData, setEvalData] = useState(null)
  const [error, setError] = useState(null)

  // Testing conditions
  const [lightCondition, setLightCondition] = useState("normal")
  const [distanceCondition, setDistanceCondition] = useState("medium")

  // Test-all state
  const [testingAll, setTestingAll] = useState(false)
  const [testResults, setTestResults] = useState(null)

  const runEvaluation = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("http://localhost:5000/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      })
      if (!res.ok) throw new Error(`Server responded ${res.status}`)
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      setEvalData(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  const testAllAlphabets = useCallback(() => {
    if (!evalData) return
    setTestingAll(true)
    // Simulate per-letter testing using evaluation data
    const results = evalData.per_letter.map((item) => {
      const report = evalData.classification_report[item.letter]
      return {
        letter: item.letter,
        accuracy: (item.accuracy * 100).toFixed(1),
        precision: report ? (report.precision * 100).toFixed(1) : "0.0",
        recall: report ? (report.recall * 100).toFixed(1) : "0.0",
        f1: report ? (report["f1-score"] * 100).toFixed(1) : "0.0",
        support: item.support,
        status: item.accuracy >= 0.8 ? "pass" : item.accuracy >= 0.5 ? "warn" : "fail",
      }
    })
    setTestResults(results)
    setTestingAll(false)
  }, [evalData])

  // Confusion matrix heatmap colour
  const getCmColor = (value, max) => {
    if (max === 0) return "transparent"
    const intensity = value / max
    // Use theme-aware approach: dark = white opacity, light = black opacity
    const isDark = document.documentElement.getAttribute("data-theme") === "dark"
    if (isDark) {
      return `rgba(255, 255, 255, ${intensity * 0.85})`
    }
    return `rgba(0, 0, 0, ${intensity * 0.8})`
  }

  const getCmTextColor = (value, max) => {
    if (max === 0) return "var(--text-muted)"
    const intensity = value / max
    const isDark = document.documentElement.getAttribute("data-theme") === "dark"
    if (isDark) {
      return intensity > 0.5 ? "#000000" : "#ffffff"
    }
    return intensity > 0.45 ? "#ffffff" : "#000000"
  }

  return (
    <div className="evaluation-page" id="evaluation-page">
      {/* Header */}
      <div className="eval-header">
        <h2>Model Evaluation</h2>
        <p className="eval-subtitle">
          Evaluate XGBoost model performance on the test dataset with comprehensive ML metrics.
        </p>
      </div>

      {/* Action buttons */}
      <div className="eval-actions">
        <button
          className="btn btn-primary"
          id="run-evaluation-btn"
          onClick={runEvaluation}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner-sm" />
              Evaluating…
            </>
          ) : (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
              Run Model Evaluation
            </>
          )}
        </button>

        {evalData && (
          <button
            className="btn btn-ghost"
            id="test-all-btn"
            onClick={testAllAlphabets}
            disabled={testingAll}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
            Test All Alphabets (A–Z)
          </button>
        )}
      </div>

      {error && (
        <div className="eval-error" id="eval-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {evalData && (
        <div className="eval-content">
          {/* ── Metrics Summary ── */}
          <section className="eval-section" id="metrics-summary">
            <div className="section-label">Metrics Summary</div>
            <div className="metrics-grid">
              <MetricCard label="Accuracy" value={evalData.accuracy} />
              <MetricCard label="Precision" value={evalData.precision} />
              <MetricCard label="Recall" value={evalData.recall} />
              <MetricCard label="F1-Score" value={evalData.f1_score} />
              <MetricCard label="mAP" value={evalData.mAP} />
              <div className="metric-card metric-card-info">
                <span className="metric-label">Test Samples</span>
                <span className="metric-value-raw">{evalData.test_size}</span>
              </div>
            </div>
          </section>

          {/* ── Confusion Matrix ── */}
          <section className="eval-section" id="confusion-matrix-section">
            <div className="section-label">Confusion Matrix</div>
            <div className="cm-wrapper">
              <div className="cm-container">
                {/* Column headers */}
                <div className="cm-row cm-header-row">
                  <div className="cm-corner" />
                  {evalData.labels.map((l) => (
                    <div key={l} className="cm-col-label">{l}</div>
                  ))}
                </div>
                {/* Data rows */}
                {evalData.confusion_matrix.map((row, ri) => {
                  const maxVal = Math.max(...evalData.confusion_matrix.flat())
                  return (
                    <div key={ri} className="cm-row">
                      <div className="cm-row-label">{evalData.labels[ri]}</div>
                      {row.map((val, ci) => (
                        <div
                          key={ci}
                          className="cm-cell"
                          style={{
                            backgroundColor: getCmColor(val, maxVal),
                            color: getCmTextColor(val, maxVal),
                          }}
                          title={`True: ${evalData.labels[ri]}, Pred: ${evalData.labels[ci]}, Count: ${val}`}
                        >
                          {val > 0 ? val : ""}
                        </div>
                      ))}
                    </div>
                  )
                })}
              </div>
              <div className="cm-axes">
                <span className="cm-axis-x">Predicted Label →</span>
                <span className="cm-axis-y">↑ True Label</span>
              </div>
            </div>
          </section>

          {/* ── Classification Report ── */}
          <section className="eval-section" id="classification-report-section">
            <div className="section-label">Classification Report (Per Letter)</div>
            <div className="report-table-wrap">
              <table className="report-table">
                <thead>
                  <tr>
                    <th>Letter</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1-Score</th>
                    <th>Support</th>
                  </tr>
                </thead>
                <tbody>
                  {evalData.labels.map((letter) => {
                    const row = evalData.classification_report[letter]
                    if (!row) return null
                    return (
                      <tr key={letter}>
                        <td className="report-letter">{letter}</td>
                        <td>{(row.precision * 100).toFixed(1)}%</td>
                        <td>{(row.recall * 100).toFixed(1)}%</td>
                        <td>{(row["f1-score"] * 100).toFixed(1)}%</td>
                        <td>{row.support}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </section>

          {/* ── Conditions Testing Panel ── */}
          <section className="eval-section" id="conditions-section">
            <div className="section-label">Testing Conditions</div>
            <div className="conditions-card">
              <div className="condition-group">
                <span className="control-label">Lighting</span>
                <div className="condition-options">
                  {["bright", "normal", "low_light"].map((c) => (
                    <button
                      key={c}
                      className={`condition-btn ${lightCondition === c ? "active" : ""}`}
                      onClick={() => setLightCondition(c)}
                    >
                      {c === "low_light" ? "Low Light" : c.charAt(0).toUpperCase() + c.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              <div className="condition-group">
                <span className="control-label">Distance</span>
                <div className="condition-options">
                  {["near", "medium", "far"].map((c) => (
                    <button
                      key={c}
                      className={`condition-btn ${distanceCondition === c ? "active" : ""}`}
                      onClick={() => setDistanceCondition(c)}
                    >
                      {c.charAt(0).toUpperCase() + c.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              <div className="condition-current">
                Current: <strong>{lightCondition}</strong> light, <strong>{distanceCondition}</strong> distance
              </div>
            </div>
          </section>

          {/* ── Test All Results ── */}
          {testResults && (
            <section className="eval-section" id="test-all-section">
              <div className="section-label">Per-Letter Test Results</div>
              <div className="test-results-grid">
                {testResults.map((r) => (
                  <div key={r.letter} className={`test-result-card test-${r.status}`}>
                    <div className="test-letter">{r.letter}</div>
                    <div className="test-acc">{r.accuracy}%</div>
                    <div className="test-status-badge">
                      {r.status === "pass" ? "✓ Pass" : r.status === "warn" ? "⚠ Warn" : "✗ Fail"}
                    </div>
                  </div>
                ))}
              </div>
              <div className="test-summary">
                <span>
                  <strong>Overall:</strong>{" "}
                  {testResults.filter((r) => r.status === "pass").length}/26 passed
                </span>
                <span>
                  <strong>Avg Accuracy:</strong>{" "}
                  {(testResults.reduce((s, r) => s + parseFloat(r.accuracy), 0) / 26).toFixed(1)}%
                </span>
              </div>
            </section>
          )}
        </div>
      )}

      {/* Empty state */}
      {!evalData && !loading && !error && (
        <div className="eval-empty">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="eval-empty-icon">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="12" y1="18" x2="12" y2="12" />
            <line x1="9" y1="15" x2="15" y2="15" />
          </svg>
          <p>Click <strong>"Run Model Evaluation"</strong> to evaluate model performance on the test dataset.</p>
        </div>
      )}
    </div>
  )
}

function MetricCard({ label, value }) {
  const pct = (value * 100).toFixed(1)
  return (
    <div className="metric-card">
      <span className="metric-label">{label}</span>
      <span className="metric-value">{pct}%</span>
      <div className="metric-bar-track">
        <div className="metric-bar-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}
