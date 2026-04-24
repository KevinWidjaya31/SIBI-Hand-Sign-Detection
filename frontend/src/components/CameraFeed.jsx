export default function CameraFeed({
  videoRef,
  canvasRef,
  cameraActive,
  cameraReady,
  isFullscreen,
  toggleFullscreen,
  fps,
  latency,
}) {
  return (
    <div className="camera-feed-wrapper">
      <div className="section-label">Live Feed</div>
      <div
        className={`camera-card ${!cameraActive ? "camera-off" : ""} ${isFullscreen ? "fullscreen" : ""}`}
        id="camera-card"
      >
        {!cameraReady && cameraActive && (
          <div className="camera-loading">
            <div className="spinner" />
            <span>Initializing camera…</span>
          </div>
        )}

        <div className="video-wrapper">
          <video ref={videoRef} autoPlay playsInline />
          <canvas ref={canvasRef} />
        </div>

        {/* Overlays */}
        <div className="camera-overlays">
          {cameraActive && (
            <>
              <span className="fps-badge" id="fps-badge">{fps} FPS</span>
              <span className="fps-badge" id="latency-badge">{latency}ms</span>
            </>
          )}
          <button
            className="fullscreen-btn"
            id="fullscreen-btn"
            onClick={toggleFullscreen}
            title="Toggle fullscreen"
            aria-label="Toggle fullscreen"
          >
            {isFullscreen ? (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="4 14 10 14 10 20" /><polyline points="20 10 14 10 14 4" />
                <line x1="14" y1="10" x2="21" y2="3" /><line x1="3" y1="21" x2="10" y2="14" />
              </svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="15 3 21 3 21 9" /><polyline points="9 21 3 21 3 15" />
                <line x1="21" y1="3" x2="14" y2="10" /><line x1="3" y1="21" x2="10" y2="14" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
