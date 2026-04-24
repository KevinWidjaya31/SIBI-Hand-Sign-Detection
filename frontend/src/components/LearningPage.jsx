import { useState } from "react"

const SIBI_DATA = [
  { letter: "A", desc: "Tangan mengepal dengan ibu jari di samping. (Fist with thumb to the side.)" },
  { letter: "B", desc: "Empat jari tegak rapat, ibu jari dilipat ke telapak. (Four fingers straight, thumb folded.)" },
  { letter: "C", desc: "Tangan membentuk huruf C melengkung. (Hand forms a curved C shape.)" },
  { letter: "D", desc: "Jari telunjuk tegak, jari lain menyentuh ibu jari. (Index finger up, others touch thumb.)" },
  { letter: "E", desc: "Semua jari dilipat ke telapak tangan. (All fingers curled into palm.)" },
  { letter: "F", desc: "Ibu jari dan telunjuk membentuk lingkaran, jari lain tegak. (Thumb and index form circle, others up.)" },
  { letter: "G", desc: "Telunjuk menunjuk ke samping, ibu jari sejajar. (Index points sideways, thumb parallel.)" },
  { letter: "H", desc: "Telunjuk dan jari tengah tegak horizontal. (Index and middle fingers out horizontally.)" },
  { letter: "I", desc: "Kelingking tegak, jari lain dilipat. (Pinky up, all others folded.)" },
  { letter: "J", desc: "Kelingking tegak lalu digerakkan membentuk huruf J. (Pinky up, trace a J motion.)" },
  { letter: "K", desc: "Telunjuk dan jari tengah tegak, ibu jari di antara keduanya. (Index and middle up, thumb between.)" },
  { letter: "L", desc: "Ibu jari dan telunjuk membentuk huruf L. (Thumb and index form an L shape.)" },
  { letter: "M", desc: "Tiga jari menutupi ibu jari di telapak. (Three fingers over thumb on palm.)" },
  { letter: "N", desc: "Dua jari menutupi ibu jari di telapak. (Two fingers over thumb on palm.)" },
  { letter: "O", desc: "Semua jari menyentuh ibu jari membentuk lingkaran. (All fingers touch thumb forming O.)" },
  { letter: "P", desc: "Mirip huruf K tapi mengarah ke bawah. (Similar to K but pointing downward.)" },
  { letter: "Q", desc: "Mirip huruf G tapi mengarah ke bawah. (Similar to G but pointing downward.)" },
  { letter: "R", desc: "Telunjuk dan jari tengah disilangkan. (Index and middle fingers crossed.)" },
  { letter: "S", desc: "Tangan mengepal, ibu jari di depan jari-jari. (Fist with thumb over fingers.)" },
  { letter: "T", desc: "Ibu jari di antara telunjuk dan jari tengah. (Thumb between index and middle finger.)" },
  { letter: "U", desc: "Telunjuk dan jari tengah tegak rapat. (Index and middle fingers up together.)" },
  { letter: "V", desc: "Telunjuk dan jari tengah tegak membentuk V. (Index and middle fingers form V.)" },
  { letter: "W", desc: "Tiga jari tegak membentuk W. (Three fingers up forming W.)" },
  { letter: "X", desc: "Telunjuk ditekuk membentuk kait. (Index finger bent into a hook.)" },
  { letter: "Y", desc: "Ibu jari dan kelingking tegak, jari lain dilipat. (Thumb and pinky up, others folded.)" },
  { letter: "Z", desc: "Telunjuk menggambar huruf Z di udara. (Index finger traces Z in the air.)" },
]

// Simple SVG hand icon placeholder
function HandIcon() {
  return (
    <svg viewBox="0 0 64 64" className="hand-icon" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M32 56c-8 0-16-6-16-16V24a4 4 0 0 1 8 0v-8a4 4 0 0 1 8 0v-4a4 4 0 0 1 8 0v6a4 4 0 0 1 8 0v22c0 10-8 16-16 16z" />
      <line x1="24" y1="24" x2="24" y2="34" />
      <line x1="32" y1="16" x2="32" y2="34" />
      <line x1="40" y1="18" x2="40" y2="34" />
    </svg>
  )
}

export default function LearningPage() {
  const [selected, setSelected] = useState(null)

  const speak = (text) => {
    if (!("speechSynthesis" in window)) return
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = "id-ID"
    utterance.rate = 0.9
    utterance.pitch = 1
    window.speechSynthesis.speak(utterance)
  }

  return (
    <div className="learning-page" id="learning-page">
      <div className="learning-header">
        <h2>Learn SIBI Alphabet</h2>
        <p className="learning-subtitle">
          Click any letter card to see the gesture description and hear the pronunciation.
        </p>
      </div>

      <div className="alphabet-grid" id="alphabet-grid">
        {SIBI_DATA.map((item) => (
          <button
            key={item.letter}
            className={`alphabet-card ${selected?.letter === item.letter ? "selected" : ""}`}
            onClick={() => setSelected(item)}
          >
            <HandIcon />
            <span className="alphabet-letter">{item.letter}</span>
          </button>
        ))}
      </div>

      {selected && (
        <div className="letter-modal-overlay" onClick={() => setSelected(null)}>
          <div className="letter-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelected(null)} aria-label="Close">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
            <div className="modal-icon-large">
              <HandIcon />
            </div>
            <div className="modal-letter">{selected.letter}</div>
            <p className="modal-desc">{selected.desc}</p>
            <button
              className="btn btn-primary"
              onClick={() => speak(selected.letter)}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
              </svg>
              Pronounce
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
