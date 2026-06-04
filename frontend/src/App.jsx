import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import LessonPage from './pages/LessonPage'
import QuizPage from './pages/QuizPage'
import ChatPage from './pages/ChatPage'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen relative overflow-x-hidden">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/lesson/:id" element={<LessonPage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/chat" element={<ChatPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
