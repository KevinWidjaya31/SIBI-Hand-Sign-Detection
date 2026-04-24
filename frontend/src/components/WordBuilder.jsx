export default function WordBuilder({ word, onAddLetter, onClear }) {
  return (
    <div className="word-builder" id="word-builder">
      <div className="section-label">Word Builder</div>
      <div className="word-card">
        <div className="word-display" id="word-display">
          {word || <span className="word-placeholder">Start building…</span>}
        </div>
        <div className="word-actions">
          <button className="btn btn-primary" id="add-letter-btn" onClick={onAddLetter}>
            Add Letter
          </button>
          <button className="btn btn-ghost" id="clear-word-btn" onClick={onClear}>
            Clear
            <kbd>C</kbd>
          </button>
        </div>
      </div>
    </div>
  )
}
