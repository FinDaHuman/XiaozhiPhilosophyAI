import { Link } from 'react-router-dom'
import {
  ArrowRight,
  BookOpen,
  Bot,
  CheckCircle2,
  Compass,
  HelpCircle,
  Library,
  MessageCircle,
  Quote,
} from 'lucide-react'
import { API_BASE } from '../config'
import { SUBJECTS, SUBJECT_ORDER } from '../data/subjects'

const prompts = [
  'Giải thích mâu thuẫn biện chứng',
  'Độc quyền nhà nước là gì?',
  'Cho ví dụ đời sống',
]

const totalLessons = SUBJECT_ORDER.reduce((n, sid) => n + Object.keys(SUBJECTS[sid].lessons).length, 0)
const totalQuestions = SUBJECT_ORDER.reduce((n, sid) => n + SUBJECTS[sid].quiz.length, 0)
const totalSlides = SUBJECT_ORDER.reduce((n, sid) => n + SUBJECTS[sid].slideCount, 0)

const stats = [
  { label: 'Bài học trọng tâm', value: String(totalLessons), icon: BookOpen },
  { label: 'Câu hỏi ôn tập', value: String(totalQuestions), icon: HelpCircle },
  { label: 'Slide nguồn', value: `${totalSlides}+`, icon: Library },
]

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-background text-text">
      <section
        className="relative isolate overflow-hidden bg-cover bg-center"
        style={{ backgroundImage: "url('/images/bg.jpg')" }}
      >
        <div className="absolute inset-0 bg-[#17100d]/70" />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(23,16,13,0.16),rgba(23,16,13,0.86))]" />

        <div className="relative z-10 mx-auto flex min-h-[88vh] w-full max-w-7xl flex-col px-5 py-5 md:px-8">
          <header className="flex items-center justify-between gap-4">
            <Link to="/" className="flex min-h-11 items-center gap-3 rounded-xl text-white focus-ring">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/15 bg-white/10 backdrop-blur">
                <Bot className="h-5 w-5" aria-hidden="true" />
              </span>
              <span className="font-serif text-xl font-bold">Lily</span>
            </Link>
            <nav className="hidden items-center gap-1 rounded-2xl border border-white/10 bg-white/10 p-1 backdrop-blur md:flex">
              <a href="#study" className="nav-link text-white/80 hover:bg-white/10 hover:text-white">
                Bài học
              </a>
              <Link to="/chat" className="nav-link text-white/80 hover:bg-white/10 hover:text-white">
                Chat
              </Link>
              <Link to="/quiz" className="nav-link text-white/80 hover:bg-white/10 hover:text-white">
                Ôn tập
              </Link>
            </nav>
          </header>

          <div className="grid flex-1 items-center gap-10 py-12 lg:grid-cols-[1.1fr_0.9fr] lg:py-16">
            <div className="max-w-3xl text-white">
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-semibold text-white/85 backdrop-blur">
                <Compass className="h-4 w-4" aria-hidden="true" />
                Trợ lý Triết học & Kinh tế chính trị Mác - Lênin
              </div>
              <h1 className="heading-balance font-serif text-5xl font-bold leading-[1.02] md:text-7xl">
                Học lý luận bằng đối thoại, nguồn rõ ràng, ví dụ gần đời sống.
              </h1>
              <p className="body-pretty mt-6 max-w-2xl text-lg leading-8 text-white/80 md:text-xl">
                Lily giúp bạn đọc slide, hỏi lại khái niệm khó, kiểm tra mức hiểu — từ quy luật mâu thuẫn
                của phép biện chứng đến lý luận cạnh tranh và độc quyền của Lênin.
              </p>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <button 
                  onClick={async () => {
                    try {
                      await fetch(`${API_BASE}/api/start-mcp`, { method: 'POST' });
                    } catch (e) {
                      console.error("Failed to start MCP:", e);
                    }
                    window.location.href = '/chat';
                  }}
                  className="clay-btn bg-white text-text hover:bg-white/95"
                >
                  <MessageCircle className="h-5 w-5" aria-hidden="true" />
                  Hỏi Lily ngay
                </button>
                <a
                  href="#study"
                  className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-white/20 bg-white/10 px-4 py-2 font-semibold text-white backdrop-blur transition-[background-color,transform] duration-150 hover:bg-white/15 active:scale-[0.98] focus-ring"
                >
                  Xem lộ trình học
                  <ArrowRight className="h-5 w-5" aria-hidden="true" />
                </a>
              </div>

              <div className="mt-8 flex flex-wrap gap-2" aria-label="Gợi ý câu hỏi">
                {prompts.map((prompt) => (
                  <Link
                    key={prompt}
                    to="/chat"
                    className="rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-medium text-white/80 backdrop-blur transition-[background-color,color] duration-150 hover:bg-white/15 hover:text-white focus-ring"
                  >
                    {prompt}
                  </Link>
                ))}
              </div>
            </div>

            <aside className="study-panel p-5 md:p-6" aria-label="Bàn học hôm nay">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="eyebrow">Bàn học hôm nay</p>
                  <h2 className="mt-2 font-serif text-3xl font-bold text-text">Bắt đầu từ câu hỏi bạn chưa chắc.</h2>
                </div>
                <Quote className="h-8 w-8 text-primary/35" aria-hidden="true" />
              </div>

              <div className="mt-6 grid gap-3 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
                {stats.map(({ label, value, icon: Icon }) => (
                  <div key={label} className="rounded-xl border border-text/10 bg-white/55 p-4">
                    <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
                    <div className="mt-3 font-serif text-3xl font-bold tabular-nums">{value}</div>
                    <div className="mt-1 text-sm font-medium text-muted">{label}</div>
                  </div>
                ))}
              </div>

              <div className="mt-6 divide-y divide-text/10 rounded-2xl border border-text/10 bg-white/55">
                <Link
                  to="/lesson/mln111/1"
                  className="flex items-center justify-between gap-4 p-4 transition-[background-color] duration-150 hover:bg-primary/5 focus-ring"
                >
                  <span>
                    <span className="block font-semibold">Triết học: Quy luật mâu thuẫn</span>
                    <span className="mt-1 block text-sm text-muted">Đi từ khái niệm đến vận dụng phương pháp luận.</span>
                  </span>
                  <ArrowRight className="h-5 w-5 text-primary" aria-hidden="true" />
                </Link>
                <Link
                  to="/lesson/ktct/1"
                  className="flex items-center justify-between gap-4 p-4 transition-[background-color] duration-150 hover:bg-primary/5 focus-ring"
                >
                  <span>
                    <span className="block font-semibold">Kinh tế chính trị: Cạnh tranh & Độc quyền</span>
                    <span className="mt-1 block text-sm text-muted">Lý luận độc quyền của Lênin và biểu hiện mới ngày nay.</span>
                  </span>
                  <ArrowRight className="h-5 w-5 text-primary" aria-hidden="true" />
                </Link>
                <Link
                  to="/quiz"
                  className="flex items-center justify-between gap-4 p-4 transition-[background-color] duration-150 hover:bg-cta/5 focus-ring"
                >
                  <span>
                    <span className="block font-semibold">Kiểm tra kiến thức</span>
                    <span className="mt-1 block text-sm text-muted">{totalQuestions} câu trắc nghiệm ở cả hai môn học.</span>
                  </span>
                  <CheckCircle2 className="h-5 w-5 text-cta" aria-hidden="true" />
                </Link>
              </div>
            </aside>
          </div>
        </div>
      </section>

      <main id="study" className="mx-auto w-full max-w-7xl px-5 py-10 md:px-8">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="eyebrow">Lộ trình</p>
            <h2 className="mt-2 font-serif text-3xl font-bold">Hai môn học, một trợ lý</h2>
          </div>
          <Link to="/chat" className="nav-link text-primary">
            Hỏi về bài đang học
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>

        <div className="mt-6 grid gap-8 lg:grid-cols-2">
          {SUBJECT_ORDER.map((sid) => {
            const s = SUBJECTS[sid]
            const lessonIds = Object.keys(s.lessons)
            return (
              <section key={s.id} className="surface-card flex flex-col p-5 md:p-7">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <span className="inline-flex rounded-full border border-secondary/20 bg-secondary/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.14em] text-secondary">
                      {s.badge}
                    </span>
                    <h3 className="mt-3 font-serif text-3xl font-bold">{s.name}</h3>
                    <p className="mt-1 text-sm font-semibold text-muted">{s.topic}</p>
                  </div>
                </div>
                <p className="body-pretty mt-4 leading-7 text-muted">{s.tagline}</p>

                <div className="mt-6 grid flex-1 gap-3 sm:grid-cols-2">
                  {lessonIds.map((lessonId) => {
                    const lesson = s.lessons[lessonId]
                    return (
                      <Link
                        key={lessonId}
                        to={`/lesson/${s.id}/${lessonId}`}
                        className="group rounded-2xl border border-text/10 bg-white/60 p-4 transition-[background-color,border-color,transform] duration-150 hover:-translate-y-0.5 hover:border-primary/30 hover:bg-white focus-ring"
                      >
                        <span className="flex items-center justify-between gap-4">
                          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-primary/10 font-serif text-lg font-bold text-primary">
                            {lessonId}
                          </span>
                          <ArrowRight className="h-5 w-5 text-muted transition-[color,transform] duration-150 group-hover:translate-x-0.5 group-hover:text-primary" aria-hidden="true" />
                        </span>
                        <span className="mt-3 block font-serif text-xl font-bold leading-6">{lesson.shortTitle}</span>
                        <span className="mt-2 block text-xs leading-5 text-muted">{lesson.slides.length} slide nguồn</span>
                      </Link>
                    )
                  })}
                </div>

                <Link to={`/quiz/${s.id}`} className="clay-btn mt-6 bg-cta border-cta hover:bg-cta/95">
                  <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
                  Làm {s.quiz.length} câu trắc nghiệm
                </Link>
              </section>
            )
          })}
        </div>
      </main>
    </div>
  )
}

export default LandingPage
