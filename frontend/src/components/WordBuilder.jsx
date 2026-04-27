import { useState, useCallback } from "react"

/**
 * WordBuilder – builds words from detected letters,
 * with Text-to-Speech (TTS) for the full constructed word.
 *
 * Uses the Web Speech API (SpeechSynthesis) with 'id-ID' locale
 * for Indonesian pronunciation.
 *
 * Props:
 *  - word: current word string
 *  - onAddLetter: callback to append the currently detected letter
 *  - onClear: callback to clear the word
 */
export default function WordBuilder({ word, onAddLetter, onClear }) {
  const [isSpeaking, setIsSpeaking] = useState(false)

  /**
   * Speak the full constructed word using browser-native TTS.
   * - Cancels any ongoing speech to prevent overlapping.
   * - Sets loading/disabled state while speaking.
   * - Uses 'id-ID' locale for Indonesian pronunciation.
   */
  const handleSpeak = useCallback(() => {
    if (!word || isSpeaking) return
    if (!("speechSynthesis" in window)) {
      console.warn("SpeechSynthesis API not supported in this browser.")
      return
    }

    // Cancel any ongoing speech to prevent overlap
    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(word)
    utterance.lang = "id-ID" // Indonesian locale
    utterance.rate = 0.9
    utterance.pitch = 1

    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)

    window.speechSynthesis.speak(utterance)
  }, [word, isSpeaking])

  return (
    <div className="word-builder" id="word-builder">
      <div className="section-label">Word Builder</div>
      <div className="word-card">
        <div className="word-display" id="word-display">
          {word || <span className="word-placeholder">Start building…</span>}
        </div>
        <div className="word-actions">
          <button
            className="btn btn-primary"
            id="add-letter-btn"
            onClick={onAddLetter}
          >
            Add Letter
            <kbd>A</kbd>
          </button>

          {/* TTS Button – speaks the FULL word, not letter-by-letter */}
          <button
            className={`btn btn-tts ${isSpeaking ? "btn-tts-active" : ""}`}
            id="tts-word-btn"
            onClick={handleSpeak}
            disabled={!word || isSpeaking}
            title={isSpeaking ? "Speaking…" : "Speak word"}
            aria-label="Speak word"
          >
            {isSpeaking ? (
              <>
                <span className="tts-spinner" />
                Speaking…
              </>
            ) : (
              <>
                {/* Speaker / volume icon */}
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                  <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
                  <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
                </svg>
                Speak
              </>
            )}
          </button>

          <button
            className="btn btn-ghost"
            id="clear-word-btn"
            onClick={onClear}
          >
            Clear
            <kbd>C</kbd>
          </button>
        </div>
      </div>
    </div>
  )
}
