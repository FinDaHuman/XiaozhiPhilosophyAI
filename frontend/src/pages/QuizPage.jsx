import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, BookOpen, CheckCircle2, HelpCircle, RotateCcw, Target, Trophy, XCircle } from 'lucide-react'
import quizData from '../data/quiz.json'

const QuizPage = () => {
  const [answers, setAnswers] = useState({})
  
  const handleSelect = (qIndex, optionId) => {
    if (answers[qIndex]) return
    setAnswers(prev => ({ ...prev, [qIndex]: optionId }))
  }

  const answeredCount = Object.keys(answers).length
  const score = Object.keys(answers).filter(
    idx => answers[idx] === quizData[idx].correctAnswer
  ).length
  const wrongCount = answeredCount - score
  const progress = Math.round((answeredCount / quizData.length) * 100)
  const isComplete = answeredCount === quizData.length

  const topicProgress = useMemo(() => {
    const groups = [
      { label: 'Nền tảng', from: 1, to: 10 },
      { label: 'Thống nhất', from: 11, to: 18 },
      { label: 'Đấu tranh', from: 19, to: 26 },
      { label: 'Phân loại', from: 27, to: 34 },
      { label: 'Phương pháp', from: 35, to: 40 },
    ]

    return groups.map(group => {
      const questions = quizData.filter(q => Number(q.id) >= group.from && Number(q.id) <= group.to)
      const answered = questions.filter(q => answers[quizData.indexOf(q)]).length
      return { ...group, answered, total: questions.length }
    })
  }, [answers])

  const resetQuiz = () => setAnswers({})

  return (
    <div className="min-h-screen bg-background pb-16">
      <header className="sticky top-0 z-40 border-b border-text/10 bg-paper/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3 md:px-6">
          <Link to="/" className="nav-link focus-ring">
            <ArrowLeft className="h-5 w-5" aria-hidden="true" />
            Trang chủ
          </Link>
          <div className="text-center">
            <p className="hidden text-xs font-bold uppercase tracking-[0.18em] text-secondary md:block">Tự kiểm tra</p>
            <h1 className="font-serif text-lg font-bold text-text md:text-2xl">Kiểm Tra Kiến Thức</h1>
          </div>
          <div className="rounded-full border border-cta/20 bg-cta/10 px-3 py-1.5 text-sm font-bold text-cta tabular-nums md:px-4">
            {score} / {quizData.length}
          </div>
        </div>
        <div className="h-1 bg-parchment">
          <div className="h-full bg-cta transition-[width] duration-300" style={{ width: `${progress}%` }} />
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl gap-6 px-4 py-6 md:px-6 lg:grid-cols-[300px_minmax(0,1fr)]">
        <aside className="lg:sticky lg:top-24 lg:self-start">
          <div className="surface-card p-5">
            <p className="eyebrow">Điểm hiện tại</p>
            <div className="mt-4 grid grid-cols-3 gap-3 text-center lg:grid-cols-1 lg:text-left">
              <div className="rounded-xl border border-text/10 bg-white/60 p-3">
                <Trophy className="mx-auto h-5 w-5 text-cta lg:mx-0" aria-hidden="true" />
                <p className="mt-2 font-serif text-2xl font-bold tabular-nums">{score}</p>
                <p className="text-xs font-semibold text-muted">Đúng</p>
              </div>
              <div className="rounded-xl border border-text/10 bg-white/60 p-3">
                <XCircle className="mx-auto h-5 w-5 text-primary lg:mx-0" aria-hidden="true" />
                <p className="mt-2 font-serif text-2xl font-bold tabular-nums">{wrongCount}</p>
                <p className="text-xs font-semibold text-muted">Sai</p>
              </div>
              <div className="rounded-xl border border-text/10 bg-white/60 p-3">
                <Target className="mx-auto h-5 w-5 text-secondary lg:mx-0" aria-hidden="true" />
                <p className="mt-2 font-serif text-2xl font-bold tabular-nums">{answeredCount}</p>
                <p className="text-xs font-semibold text-muted">Đã làm</p>
              </div>
            </div>

            <div className="mt-5 space-y-3">
              {topicProgress.map(topic => (
                <div key={topic.label}>
                  <div className="mb-1 flex items-center justify-between text-xs font-semibold text-muted">
                    <span>{topic.label}</span>
                    <span className="tabular-nums">{topic.answered}/{topic.total}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-parchment">
                    <div
                      className="h-full rounded-full bg-secondary"
                      style={{ width: `${Math.round((topic.answered / topic.total) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <button
              type="button"
              onClick={resetQuiz}
              className="mt-6 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl border border-text/10 bg-paper px-4 py-2 font-semibold text-text shadow-soft transition-[background-color,transform] duration-150 hover:bg-white active:scale-[0.98] focus-ring"
            >
              <RotateCcw className="h-5 w-5" aria-hidden="true" />
              Làm lại
            </button>
          </div>
        </aside>

        <section className="min-w-0 space-y-6">
          <div className="study-panel p-5 md:p-7">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="eyebrow">Ôn tập có phản hồi</p>
                <h2 className="heading-balance mt-2 font-serif text-4xl font-bold">
                  {isComplete ? 'Bạn đã hoàn thành bài kiểm tra.' : 'Chọn đáp án, rồi đọc lại lý do.'}
                </h2>
                <p className="body-pretty mt-3 max-w-3xl leading-7 text-muted">
                  Mỗi câu sẽ khóa sau khi chọn để mô phỏng kiểm tra thật. Phần phản hồi cho bạn biết đáp án đúng để quay lại học sâu hơn.
                </p>
              </div>
              {isComplete && (
                <div className="rounded-2xl border border-cta/20 bg-cta/10 p-4 text-cta">
                  <p className="font-serif text-4xl font-bold tabular-nums">{Math.round((score / quizData.length) * 100)}%</p>
                  <p className="mt-1 text-sm font-bold">Tỉ lệ chính xác</p>
                </div>
              )}
            </div>
          </div>

          {quizData.map((q, qIndex) => {
            const isAnswered = answers[qIndex] !== undefined
            const selected = answers[qIndex]
            const isCorrect = selected === q.correctAnswer
            const correctOption = q.options.find(opt => opt.id === q.correctAnswer)

            return (
              <article key={q.id} className="surface-card overflow-hidden">
                <div className="border-b border-text/10 bg-paper px-5 py-4">
                  <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                    <div>
                      <p className="mb-2 flex items-center gap-2 text-sm font-bold text-secondary">
                        <HelpCircle className="h-4 w-4" aria-hidden="true" />
                        Câu {q.id}
                      </p>
                      <h3 className="heading-balance text-lg font-bold leading-7 text-text md:text-xl">
                        {q.text}
                      </h3>
                    </div>
                    {isAnswered && (
                      <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-bold ${isCorrect ? 'bg-cta/10 text-cta' : 'bg-primary/10 text-primary'}`}>
                        {isCorrect ? <CheckCircle2 className="h-4 w-4" aria-hidden="true" /> : <XCircle className="h-4 w-4" aria-hidden="true" />}
                        {isCorrect ? 'Đúng' : 'Cần ôn lại'}
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="space-y-3 p-5">
                  {q.options.map((opt) => {
                    let btnClass = "w-full rounded-xl border p-4 text-left shadow-soft transition-[background-color,border-color,box-shadow,transform] duration-150 focus-ring "
                    
                    if (!isAnswered) {
                      btnClass += "border-text/10 bg-white hover:-translate-y-0.5 hover:border-primary/30 hover:bg-primary/5 hover:shadow-paper"
                    } else if (opt.id === q.correctAnswer) {
                      btnClass += "border-cta/50 bg-cta/10 text-cta"
                    } else if (opt.id === selected) {
                      btnClass += "border-primary/50 bg-primary/10 text-primary"
                    } else {
                      btnClass += "border-text/10 bg-white/50 text-muted opacity-70"
                    }

                    return (
                      <button
                        key={opt.id}
                        type="button"
                        onClick={() => handleSelect(qIndex, opt.id)}
                        disabled={isAnswered}
                        className={btnClass}
                        aria-pressed={selected === opt.id}
                      >
                        <span className="flex items-center justify-between gap-4">
                          <span className="font-medium leading-6">{opt.id}. {opt.text}</span>
                          {isAnswered && opt.id === q.correctAnswer && <CheckCircle2 className="h-6 w-6 shrink-0" aria-hidden="true" />}
                          {isAnswered && opt.id === selected && opt.id !== q.correctAnswer && <XCircle className="h-6 w-6 shrink-0" aria-hidden="true" />}
                        </span>
                      </button>
                    )
                  })}

                  {isAnswered && (
                    <div className={`rounded-2xl border p-4 ${isCorrect ? 'border-cta/20 bg-cta/5' : 'border-primary/20 bg-primary/5'}`}>
                      <p className="flex items-center gap-2 font-bold">
                        <BookOpen className={`h-5 w-5 ${isCorrect ? 'text-cta' : 'text-primary'}`} aria-hidden="true" />
                        {isCorrect ? 'Bạn đã nắm đúng ý chính.' : 'Đáp án cần nhớ'}
                      </p>
                      <p className="mt-2 leading-7 text-muted">
                        Đáp án đúng là <span className="font-bold text-text">{correctOption?.id}. {correctOption?.text}</span>. Nếu còn phân vân, hãy hỏi XiaoZhi giải thích lại bằng ví dụ hoặc quay về bài học liên quan.
                      </p>
                      <Link to="/chat" className="mt-3 inline-flex items-center gap-2 text-sm font-bold text-primary focus-ring">
                        Hỏi XiaoZhi về câu này
                        <ArrowLeft className="h-4 w-4 rotate-180" aria-hidden="true" />
                      </Link>
                    </div>
                  )}
                </div>
              </article>
            )
          })}
        </section>
      </main>
    </div>
  )
}

export default QuizPage
