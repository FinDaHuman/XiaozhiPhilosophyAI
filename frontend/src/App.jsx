import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import LessonPage from './pages/LessonPage'
import QuizPage from './pages/QuizPage'
import ChatPage from './pages/ChatPage'

// SPA navigation keeps the previous scroll position; reset to top on every route change
function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])
  return null
}

function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <div className="min-h-screen relative overflow-x-hidden">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          {/* Legacy paths (no subject) default to the philosophy subject */}
          <Route path="/lesson/:id" element={<LessonPage />} />
          <Route path="/lesson/:subject/:id" element={<LessonPage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/quiz/:subject" element={<QuizPage />} />
          <Route path="/chat" element={<ChatPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
