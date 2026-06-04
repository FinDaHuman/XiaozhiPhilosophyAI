import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, XCircle } from 'lucide-react'
import quizData from '../data/quiz.json'

const QuizPage = () => {
  const [answers, setAnswers] = useState({}) // { [questionIndex]: selectedOptionId }
  
  const handleSelect = (qIndex, optionId) => {
    if (answers[qIndex]) return; // prevent re-answering
    setAnswers(prev => ({ ...prev, [qIndex]: optionId }))
  }

  const score = Object.keys(answers).filter(
    idx => answers[idx] === quizData[idx].correctAnswer
  ).length

  return (
    <div className="min-h-screen bg-background pb-20">
      <div className="bg-white shadow-sm sticky top-0 z-40 border-b-2 border-secondary/20">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center text-primary font-bold hover:opacity-80 transition-opacity">
            <ArrowLeft className="w-5 h-5 mr-1" />
            Trang chủ
          </Link>
          <h1 className="text-xl md:text-2xl font-bold text-text">Kiểm Tra Kiến Thức</h1>
          <div className="font-bold text-cta bg-cta/10 px-4 py-1 rounded-full">
            {score} / {quizData.length}
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
        {quizData.map((q, qIndex) => {
          const isAnswered = answers[qIndex] !== undefined
          const selected = answers[qIndex]
          const isCorrect = selected === q.correctAnswer

          return (
            <div key={q.id} className="clay-card p-6">
              <h3 className="text-lg font-bold text-text mb-4">
                Câu {q.id}: {q.text}
              </h3>
              
              <div className="space-y-3">
                {q.options.map((opt) => {
                  let btnClass = "w-full text-left p-4 rounded-xl border-2 transition-all duration-200 shadow-sm "
                  
                  if (!isAnswered) {
                    btnClass += "border-secondary/20 bg-white hover:border-primary hover:bg-primary/5 hover:shadow-md cursor-pointer"
                  } else {
                    if (opt.id === q.correctAnswer) {
                      btnClass += "border-green-500 bg-green-50 text-green-900 shadow-inner"
                    } else if (opt.id === selected) {
                      btnClass += "border-red-500 bg-red-50 text-red-900 shadow-inner"
                    } else {
                      btnClass += "border-secondary/10 bg-white opacity-50 cursor-not-allowed"
                    }
                  }

                  return (
                    <button
                      key={opt.id}
                      onClick={() => handleSelect(qIndex, opt.id)}
                      disabled={isAnswered}
                      className={btnClass}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium mr-2">{opt.id}. {opt.text}</span>
                        {isAnswered && opt.id === q.correctAnswer && <CheckCircle2 className="w-6 h-6 text-green-500 flex-shrink-0" />}
                        {isAnswered && opt.id === selected && opt.id !== q.correctAnswer && <XCircle className="w-6 h-6 text-red-500 flex-shrink-0" />}
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default QuizPage
