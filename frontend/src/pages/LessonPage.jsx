import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ArrowRight, BookOpen, Bot, CheckCircle2, FileText, MessageCircle } from 'lucide-react'
import { getSubject } from '../data/subjects'

const LessonPage = () => {
  // Route is either /lesson/:id (legacy, philosophy) or /lesson/:subject/:id
  const { subject: subjectParam, id } = useParams()
  const subject = getSubject(subjectParam)
  const lessonData = subject.lessons
  const lesson = lessonData[id]

  const lessonPath = (lessonId) => `/lesson/${subject.id}/${lessonId}`

  if (!lesson) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-6 text-center">
        <div className="surface-card max-w-md p-8">
          <h1 className="font-serif text-3xl font-bold">Không tìm thấy bài học</h1>
          <p className="mt-3 text-muted">Bài học này chưa có trong lộ trình hiện tại.</p>
          <Link to="/" className="clay-btn mt-6">Về trang chủ</Link>
        </div>
      </div>
    )
  }

  const lessonOrder = Object.keys(lessonData)
  const activeIndex = lessonOrder.indexOf(id)
  const prevId = activeIndex > 0 ? lessonOrder[activeIndex - 1] : null
  const nextId = activeIndex < lessonOrder.length - 1 ? lessonOrder[activeIndex + 1] : null
  const progress = Math.round(((activeIndex + 1) / lessonOrder.length) * 100)

  return (
    <div className="min-h-screen bg-background pb-16">
      <header className="sticky top-0 z-40 border-b border-text/10 bg-paper/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3 md:px-6">
          <Link to="/" className="nav-link focus-ring">
            <ArrowLeft className="h-5 w-5" aria-hidden="true" />
            Trang chủ
          </Link>
          <div className="min-w-0 text-center">
            <p className="hidden text-xs font-bold uppercase tracking-[0.18em] text-secondary md:block">{subject.topic}</p>
            <h1 className="truncate font-serif text-lg font-bold text-text md:text-2xl">{lesson.title}</h1>
          </div>
          <div className="flex gap-2">
            {prevId ? (
              <Link to={lessonPath(prevId)} className="icon-button focus-ring" aria-label="Bài trước">
                <ArrowLeft className="h-5 w-5" aria-hidden="true" />
              </Link>
            ) : <div className="h-11 w-11" />}
            {nextId ? (
              <Link to={lessonPath(nextId)} className="icon-button focus-ring" aria-label="Bài tiếp theo">
                <ArrowRight className="h-5 w-5" aria-hidden="true" />
              </Link>
            ) : <div className="h-11 w-11" />}
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-7xl gap-6 px-4 py-6 md:px-6 lg:grid-cols-[300px_minmax(0,1fr)]">
        <aside className="lg:sticky lg:top-24 lg:self-start">
          <div className="surface-card overflow-hidden">
            <div className="border-b border-text/10 p-5">
              <p className="eyebrow">{subject.badge} · Tiến độ</p>
              <div className="mt-3 flex items-end justify-between gap-4">
                <span className="font-serif text-4xl font-bold tabular-nums">{progress}%</span>
                <span className="text-sm font-semibold text-muted">Bài {activeIndex + 1}/{lessonOrder.length}</span>
              </div>
              <div className="mt-4 h-2 overflow-hidden rounded-full bg-parchment">
                <div className="h-full rounded-full bg-primary" style={{ width: `${progress}%` }} />
              </div>
            </div>
            <nav className="divide-y divide-text/10" aria-label="Danh sách bài học">
              {lessonOrder.map((lessonId) => {
                const item = lessonData[lessonId]
                const isActive = lessonId === id
                return (
                  <Link
                    key={lessonId}
                    to={lessonPath(lessonId)}
                    className={`flex items-start gap-3 p-4 transition-[background-color,color] duration-150 focus-ring ${isActive ? 'bg-primary/10 text-primary' : 'hover:bg-text/5'}`}
                  >
                    <span className={`mt-0.5 inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-sm font-bold ${isActive ? 'bg-primary text-white' : 'bg-text/5 text-muted'}`}>
                      {lessonId}
                    </span>
                    <span>
                      <span className="block font-semibold">{item.shortTitle}</span>
                      <span className="mt-1 block text-xs leading-5 text-muted">{item.slides.length} slide nguồn</span>
                    </span>
                  </Link>
                )
              })}
            </nav>
          </div>
        </aside>

        <section className="min-w-0 space-y-6">
          <div className="study-panel overflow-hidden">
            <div className="grid gap-6 p-5 md:p-7 lg:grid-cols-[1fr_260px]">
              <div>
                <p className="eyebrow">{subject.name}</p>
                <h2 className="heading-balance mt-2 font-serif text-4xl font-bold md:text-5xl">{lesson.shortTitle}</h2>
                <p className="body-pretty mt-4 max-w-3xl text-lg leading-8 text-muted">{lesson.summary}</p>
                <div className="mt-5 flex flex-wrap gap-2">
                  {lesson.concepts.map((concept) => (
                    <span key={concept} className="rounded-full border border-secondary/20 bg-secondary/10 px-3 py-1.5 text-sm font-semibold text-secondary">
                      {concept}
                    </span>
                  ))}
                </div>
              </div>
              <div className="rounded-2xl border border-text/10 bg-white/60 p-4">
                <FileText className="h-6 w-6 text-primary" aria-hidden="true" />
                <p className="mt-3 text-sm font-bold text-text">Cách học gợi ý</p>
                <p className="mt-2 text-sm leading-6 text-muted">
                  Xem slide trước, ghi lại khái niệm chưa rõ, rồi hỏi Lily bằng ngôn ngữ của bạn.
                </p>
                <Link to="/chat" className="mt-4 inline-flex items-center gap-2 text-sm font-bold text-primary focus-ring">
                  <MessageCircle className="h-4 w-4" aria-hidden="true" />
                  Hỏi về bài này
                </Link>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            {lesson.slides.map((slideNum, index) => (
              <figure key={slideNum} className="surface-card overflow-hidden">
                <figcaption className="flex flex-col gap-3 border-b border-text/10 bg-paper px-4 py-3 md:flex-row md:items-center md:justify-between md:px-5">
                  <div className="flex items-center gap-3">
                    <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-primary/10 text-primary">
                      <BookOpen className="h-5 w-5" aria-hidden="true" />
                    </span>
                    <div>
                      <p className="font-serif text-lg font-bold">
                        {subject.id === 'ktct' ? `Slide KTCT ${slideNum}` : `Slide ${slideNum}`}
                      </p>
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted">Nguồn {index + 1}/{lesson.slides.length}</p>
                    </div>
                  </div>
                  <Link to="/chat" className="inline-flex items-center gap-2 text-sm font-bold text-primary focus-ring">
                    <Bot className="h-4 w-4" aria-hidden="true" />
                    Hỏi slide này
                  </Link>
                </figcaption>
                <div className="bg-[#f1eadf] p-2 md:p-4">
                  <img
                    src={`${subject.slideDir}/slide_${slideNum}.jpg`}
                    alt={`Slide ${slideNum} của ${lesson.title}`}
                    className="mx-auto h-auto w-full rounded-xl"
                    loading="lazy"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 600' fill='none'%3E%3Crect width='800' height='600' fill='%23f1eadf'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='24' fill='%236F6259'%3EHình ảnh slide chưa cập nhật%3C/text%3E%3C/svg%3E";
                    }}
                  />
                </div>
              </figure>
            ))}
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:justify-between">
            {prevId ? (
              <Link to={lessonPath(prevId)} className="clay-btn bg-paper text-text hover:bg-white">
                <ArrowLeft className="h-5 w-5" aria-hidden="true" />
                Bài trước
              </Link>
            ) : <span />}
            {nextId ? (
              <Link to={lessonPath(nextId)} className="clay-btn">
                Bài tiếp theo
                <ArrowRight className="h-5 w-5" aria-hidden="true" />
              </Link>
            ) : (
              <Link to={`/quiz/${subject.id}`} className="clay-btn bg-cta border-cta hover:bg-cta/95">
                <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
                Làm bài ôn tập
              </Link>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

export default LessonPage
