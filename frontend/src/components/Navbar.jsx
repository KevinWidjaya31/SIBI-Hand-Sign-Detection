import { useState } from "react"

export default function Navbar({ activeTab, setActiveTab, theme, toggleTheme }) {
  const [shortcutsOpen, setShortcutsOpen] = useState(false)

  return (
    <nav className="navbar" id="navbar">
      <div className="nav-left">
        <span className="nav-logo" aria-hidden="true">◉</span>
        <span className="nav-brand">SIBI</span>
      </div>

      <div className="nav-tabs">
        <button
          id="tab-detection"
          className={`nav-tab ${activeTab === "detection" ? "active" : ""}`}
          onClick={() => setActiveTab("detection")}
        >
          Detection
        </button>
        <button
          id="tab-learn"
          className={`nav-tab ${activeTab === "learn" ? "active" : ""}`}
          onClick={() => setActiveTab("learn")}
        >
          Learn SIBI
        </button>
        <button
          id="tab-evaluation"
          className={`nav-tab ${activeTab === "evaluation" ? "active" : ""}`}
          onClick={() => setActiveTab("evaluation")}
        >
          Evaluation
        </button>
      </div>

      <div className="nav-right">
        <button
          className="nav-icon-btn"
          id="shortcuts-btn"
          onClick={() => setShortcutsOpen(!shortcutsOpen)}
          title="Keyboard shortcuts"
          aria-label="Keyboard shortcuts"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="4" width="20" height="16" rx="2" />
            <path d="M6 8h.01M10 8h.01M14 8h.01M18 8h.01M6 12h.01M10 12h.01M14 12h.01M18 12h.01M8 16h8" />
          </svg>
        </button>

        <button
          className="nav-icon-btn"
          id="theme-toggle"
          onClick={toggleTheme}
          title={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
          aria-label="Toggle theme"
        >
          {theme === "light" ? (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="5" />
              <line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" />
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
              <line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" />
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>
          )}
        </button>

        {shortcutsOpen && (
          <div className="shortcuts-dropdown" id="shortcuts-dropdown">
            <div className="shortcut-row"><kbd>S</kbd><span>Start / Stop camera</span></div>
            <div className="shortcut-row"><kbd>C</kbd><span>Clear word</span></div>
            <div className="shortcut-row"><kbd>A</kbd><span>Add letter to word</span></div>
          </div>
        )}
      </div>
    </nav>
  )
}
