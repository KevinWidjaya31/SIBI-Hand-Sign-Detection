import { useEffect, useRef, useState, useCallback } from "react"
import { Hands, HAND_CONNECTIONS } from "@mediapipe/hands"
import { Camera } from "@mediapipe/camera_utils"
import { drawConnectors, drawLandmarks } from "@mediapipe/drawing_utils"

import CameraFeed from "./CameraFeed"
import ResultPanel from "./ResultPanel"
import WordBuilder from "./WordBuilder"
import HistoryLog from "./HistoryLog"
import ControlPanel from "./ControlPanel"

let historyId = 0

export default function DetectionPage() {
  const videoRef = useRef(null)
  const handsRef = useRef(null)
  const cameraRef = useRef(null)
  const canvasRef = useRef(null)

  const [letter, setLetter] = useState("-")
  const [confidence, setConfidence] = useState(0)
  const [cameraActive, setCameraActive] = useState(true)
  const [cameraReady, setCameraReady] = useState(false)

  // New feature states
  const [top3, setTop3] = useState([])
  const [history, setHistory] = useState([])
  const [word, setWord] = useState("")
  const [ttsEnabled, setTtsEnabled] = useState(true)
  const [threshold, setThreshold] = useState(70)
  const [fps, setFps] = useState(0)
  const [stability, setStability] = useState("Unstable")
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [latency, setLatency] = useState(0)

  const lastLetterRef = useRef(null)
  const lastSpeakTimeRef = useRef(0)
  const stabilityCountRef = useRef(0)
  const prevLetterRef = useRef(null)
  const frameTimesRef = useRef([])
  const ttsEnabledRef = useRef(ttsEnabled)
  const thresholdRef = useRef(threshold)

  // Keep refs in sync with state so the MediaPipe callback reads latest values
  useEffect(() => { ttsEnabledRef.current = ttsEnabled }, [ttsEnabled])
  useEffect(() => { thresholdRef.current = threshold }, [threshold])

  // Frontend TTS
  const speak = (text) => {
    if (!("speechSynthesis" in window)) return

    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = "id-ID"
    utterance.rate = 0.9
    utterance.pitch = 1
    window.speechSynthesis.speak(utterance)
  }

  // Draw landmarks on canvas
  const drawHandLandmarks = useCallback((landmarks, canvas, video) => {
    if (!canvas || !video) return
    const ctx = canvas.getContext("2d")
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Determine theme for landmark colour
    const isDark = document.documentElement.getAttribute("data-theme") === "dark"
    const dotColor = isDark ? "#ffffff" : "#000000"
    const lineColor = isDark ? "rgba(255,255,255,0.4)" : "rgba(0,0,0,0.35)"

    drawConnectors(ctx, landmarks, HAND_CONNECTIONS, { color: lineColor, lineWidth: 2 })
    drawLandmarks(ctx, landmarks, { color: dotColor, lineWidth: 1, radius: 3 })
  }, [])

  // FPS calculation
  const updateFps = useCallback(() => {
    const now = performance.now()
    frameTimesRef.current.push(now)
    // Keep only last 30 timestamps
    if (frameTimesRef.current.length > 30) frameTimesRef.current.shift()
    if (frameTimesRef.current.length >= 2) {
      const elapsed = now - frameTimesRef.current[0]
      const count = frameTimesRef.current.length - 1
      setFps(Math.round((count / elapsed) * 1000))
    }
  }, [])

  useEffect(() => {
    if (handsRef.current) return // cegah init ulang

    const hands = new Hands({
      locateFile: (file) =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4/${file}`,
    })

    hands.setOptions({
      maxNumHands: 1,
      modelComplexity: 1,
      minDetectionConfidence: 0.6,
      minTrackingConfidence: 0.5,
    })

    hands.onResults(async (results) => {
      updateFps()

      if (
        !results.multiHandLandmarks ||
        results.multiHandLandmarks.length === 0
      ) {
        setLetter("-")
        setConfidence(0)
        setTop3([])
        // Clear canvas
        if (canvasRef.current && videoRef.current) {
          const ctx = canvasRef.current.getContext("2d")
          canvasRef.current.width = videoRef.current.videoWidth
          canvasRef.current.height = videoRef.current.videoHeight
          ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)
        }
        return
      }

      const lm = results.multiHandLandmarks[0]
      if (!lm || lm.length !== 21) return

      // Draw landmarks
      drawHandLandmarks(lm, canvasRef.current, videoRef.current)

      const xs = lm.map((p) => p.x)
      const ys = lm.map((p) => p.y)

      const minX = Math.min(...xs)
      const minY = Math.min(...ys)

      const landmarks = []
      lm.forEach((p) => {
        landmarks.push(p.x - minX)
        landmarks.push(p.y - minY)
      })

      try {
        const inferStart = performance.now()
        const res = await fetch("http://localhost:5000/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ landmarks }),
        })

        if (!res.ok) return

        const data = await res.json()
        const inferEnd = performance.now()
        setLatency(Math.round(inferEnd - inferStart))
        const labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        const detectedLetter = labels[data.prediction]

        setLetter(detectedLetter)
        setConfidence(data.confidence)

        // Top-3
        if (data.top3) {
          setTop3(data.top3)
        }

        // Stability tracking
        if (detectedLetter === prevLetterRef.current) {
          stabilityCountRef.current++
        } else {
          stabilityCountRef.current = 0
        }
        prevLetterRef.current = detectedLetter
        setStability(stabilityCountRef.current >= 5 ? "Stable" : "Unstable")

        // History
        if (
          detectedLetter !== lastLetterRef.current &&
          data.confidence > thresholdRef.current
        ) {
          setHistory((prev) => {
            const next = [
              { letter: detectedLetter, time: new Date().toLocaleTimeString(), id: ++historyId },
              ...prev,
            ]
            return next.slice(0, 15)
          })
        }

        const now = Date.now()
        if (
          detectedLetter !== lastLetterRef.current &&
          data.confidence > thresholdRef.current &&
          now - lastSpeakTimeRef.current > 1200
        ) {
          if (ttsEnabledRef.current) {
            speak(detectedLetter)
          }
          lastLetterRef.current = detectedLetter
          lastSpeakTimeRef.current = now
        }
      } catch (err) {
        console.error("Prediction error:", err)
      }
    })

    handsRef.current = hands

    if (!videoRef.current) return

    const camera = new Camera(videoRef.current, {
      onFrame: async () => {
        if (!videoRef.current) return
        await hands.send({ image: videoRef.current })
      },
      width: 640,
      height: 480,
    })

    camera.start()
    cameraRef.current = camera
    setCameraReady(true)

    return () => {
      camera.stop()
    }
  }, [])

  const handleToggleCamera = useCallback(() => {
    if (!cameraRef.current) return
    if (cameraActive) {
      cameraRef.current.stop()
      setCameraActive(false)
      setLetter("-")
      setConfidence(0)
      setTop3([])
      setFps(0)
      frameTimesRef.current = []
    } else {
      cameraRef.current.start()
      setCameraActive(true)
    }
  }, [cameraActive])

  const handleAddLetter = useCallback(() => {
    if (letter !== "-") {
      setWord((prev) => prev + letter)
    }
  }, [letter])

  const handleClearWord = useCallback(() => {
    setWord("")
  }, [])

  const toggleFullscreen = useCallback(() => {
    setIsFullscreen((prev) => !prev)
  }, [])

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e) => {
      // Don't trigger if user is typing in an input
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return
      if (e.key === "s" || e.key === "S") {
        e.preventDefault()
        handleToggleCamera()
      }
      if (e.key === "c" || e.key === "C") {
        e.preventDefault()
        handleClearWord()
      }
      if (e.key === "a" || e.key === "A") {
        e.preventDefault()
        handleAddLetter()
      }
    }
    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [handleToggleCamera, handleClearWord, handleAddLetter])

  // Derive status
  const getStatus = () => {
    if (!cameraActive) return { text: "Camera Off", type: "off" }
    if (letter === "-") return { text: "No Hand Detected", type: "idle" }
    if (confidence > threshold) return { text: "Gesture Detected", type: "detected" }
    return { text: "Detecting…", type: "detecting" }
  }

  const status = getStatus()

  return (
    <div className="detection-page" id="detection-page">
      <div className="detection-grid">
        {/* Left Column */}
        <div className="col-left">
          <CameraFeed
            videoRef={videoRef}
            canvasRef={canvasRef}
            cameraActive={cameraActive}
            cameraReady={cameraReady}
            isFullscreen={isFullscreen}
            toggleFullscreen={toggleFullscreen}
            fps={fps}
            latency={latency}
          />
          <ControlPanel
            cameraActive={cameraActive}
            onToggleCamera={handleToggleCamera}
            ttsEnabled={ttsEnabled}
            onToggleTts={() => setTtsEnabled((p) => !p)}
            threshold={threshold}
            onThresholdChange={setThreshold}
          />
        </div>

        {/* Right Column */}
        <div className="col-right">
          <ResultPanel
            letter={letter}
            confidence={confidence}
            status={status}
            top3={top3}
            stability={stability}
            fps={fps}
            latency={latency}
          />
          <WordBuilder
            word={word}
            onAddLetter={handleAddLetter}
            onClear={handleClearWord}
          />
          <HistoryLog history={history} />
        </div>
      </div>
    </div>
  )
}
