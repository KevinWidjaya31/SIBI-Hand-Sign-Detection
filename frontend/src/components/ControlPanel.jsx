export default function ControlPanel({
  cameraActive,
  onToggleCamera,
  ttsEnabled,
  onToggleTts,
  threshold,
  onThresholdChange,
}) {
  return (
    <div className="control-panel" id="control-panel">
      <div className="section-label">Controls</div>
      <div className="controls-card">
        {/* Camera Toggle */}
        <div className="control-row">
          <span className="control-label">Camera</span>
          <button
            className={`btn ${cameraActive ? "btn-ghost" : "btn-primary"}`}
            id="toggle-camera-btn"
            onClick={onToggleCamera}
          >
            {cameraActive ? "Stop" : "Start"}
            <kbd>S</kbd>
          </button>
        </div>

        {/* TTS Toggle */}
        <div className="control-row">
          <span className="control-label">Voice (TTS)</span>
          <label className="toggle-switch" id="tts-toggle">
            <input
              type="checkbox"
              checked={ttsEnabled}
              onChange={onToggleTts}
            />
            <span className="toggle-slider" />
          </label>
        </div>

        {/* Threshold Slider */}
        <div className="control-row control-row-col">
          <div className="control-row-header">
            <span className="control-label">Confidence Threshold</span>
            <span className="control-value">{threshold}%</span>
          </div>
          <input
            type="range"
            className="range-slider"
            id="threshold-slider"
            min="0"
            max="100"
            value={threshold}
            onChange={(e) => onThresholdChange(Number(e.target.value))}
          />
        </div>
      </div>
    </div>
  )
}
