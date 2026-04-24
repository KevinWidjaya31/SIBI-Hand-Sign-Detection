import { useState, useEffect } from "react"
import Navbar from "./components/Navbar"
import DetectionPage from "./components/DetectionPage"
import LearningPage from "./components/LearningPage"
import EvaluationPage from "./components/EvaluationPage"
import "./App.css"

function App() {
  const [activeTab, setActiveTab] = useState("detection")
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("sibi-theme") || "light"
  })

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme)
    localStorage.setItem("sibi-theme", theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"))
  }

  const renderPage = () => {
    switch (activeTab) {
      case "detection":
        return <DetectionPage />
      case "learn":
        return <LearningPage />
      case "evaluation":
        return <EvaluationPage />
      default:
        return <DetectionPage />
    }
  }

  return (
    <div className="app-shell">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        theme={theme}
        toggleTheme={toggleTheme}
      />
      <main className="app-main">
        {renderPage()}
      </main>
      <footer className="app-footer" id="footer">
        <p>SIBI Recognition &middot; MediaPipe &times; XGBoost</p>
      </footer>
    </div>
  )
}

export default App
