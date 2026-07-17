import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  ArrowLeft,
  Bot,
  Brain,
  Library,
  Lightbulb,
  Loader2,
  MessageCircle,
  PanelLeft,
  Presentation,
  Send,
  Sparkles,
  User,
  X,
} from 'lucide-react'
import { apiFetch } from '../config'

const quickPrompts = [
  {
    icon: Brain,
    label: 'Giải thích khái niệm',
    prompt: 'Giải thích quy luật thống nhất và đấu tranh của các mặt đối lập theo cách dễ hiểu.',
  },
  {
    icon: Lightbulb,
    label: 'Cho ví dụ',
    prompt: 'Cho tôi một ví dụ đời sống về mâu thuẫn biện chứng và phân tích từng mặt đối lập.',
  },
  {
    icon: Library,
    label: 'Ôn theo slide',
    prompt: 'Tóm tắt các ý quan trọng nhất về phân loại mâu thuẫn và chỉ ra slide nguồn.',
  },
  {
    icon: Brain,
    label: 'Kinh tế chính trị',
    prompt: 'Trình bày các đặc điểm kinh tế của độc quyền theo Lênin và chỉ ra slide nguồn.',
  },
]

const ChatPage = () => {
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Xin chào, tôi là Lily - trợ lý AI triết học của bạn. Bạn muốn khám phá điều gì hôm nay?' }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [activeSlide, setActiveSlide] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const choosePrompt = (prompt) => {
    setInput(prompt)
    window.requestAnimationFrame(() => inputRef.current?.focus())
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: userMessage }])
    setIsLoading(true)

    try {
      const response = await apiFetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      })
      
      if (response.ok) {
        const data = await response.json()
        setMessages(prev => [...prev, { role: 'ai', text: data.answer }])
        
        // Two decks: philosophy "[Slide 12]" and political economy "[Slide KTCT 5]".
        // Pick whichever citation appears first in the answer.
        const ktctMatch = data.answer.match(/\[Slide\s*KTCT\s*(\d+)\]/i)
        const mln111Match = data.answer.match(/\[Slide\s*(\d+)\]/i)
        if (ktctMatch && (!mln111Match || ktctMatch.index <= mln111Match.index)) {
          setActiveSlide({ deck: 'ktct', num: ktctMatch[1] })
        } else if (mln111Match) {
          setActiveSlide({ deck: 'mln111', num: mln111Match[1] })
        }
      } else {
        setMessages(prev => [...prev, { role: 'ai', text: 'Xin lỗi, tôi gặp lỗi kết nối. Vui lòng thử lại sau.' }])
      }
    } catch (error) {
      console.error(error)
      setMessages(prev => [...prev, { role: 'ai', text: 'Không thể kết nối với máy chủ Lily. Vui lòng kiểm tra lại.' }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-screen min-h-screen flex-col bg-background">
      <header className="flex-shrink-0 border-b border-text/10 bg-paper/95 backdrop-blur">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-4 py-3 md:px-6">
          <Link to="/" className="nav-link focus-ring">
            <ArrowLeft className="h-5 w-5" aria-hidden="true" />
            Trang chủ
          </Link>
          <h1 className="flex items-center gap-2 font-serif text-xl font-bold text-text md:text-2xl">
            <Bot className="h-6 w-6 text-primary" aria-hidden="true" />
            Lily AI
          </h1>
          <Link to="/quiz" className="hidden nav-link text-primary focus-ring sm:inline-flex">
            Ôn tập
          </Link>
        </div>
      </header>

      <main className="mx-auto grid min-h-0 w-full max-w-7xl flex-1 gap-4 p-4 md:p-6 lg:grid-cols-[minmax(0,1fr)_360px]">
        <section className="study-panel flex min-h-0 flex-col overflow-hidden" aria-label="Cuộc trò chuyện với Lily">
          <div className="border-b border-text/10 bg-paper/90 px-4 py-4 md:px-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="eyebrow">Đối thoại học tập</p>
                <h2 className="mt-1 font-serif text-2xl font-bold">Hỏi, phản biện, rồi quay lại nguồn.</h2>
              </div>
              <div className="flex items-center gap-2 rounded-full border border-cta/20 bg-cta/10 px-3 py-1.5 text-sm font-semibold text-cta">
                <Sparkles className="h-4 w-4" aria-hidden="true" />
                Có trích dẫn slide khi tìm thấy
              </div>
            </div>
          </div>

          {activeSlide && (
            <div className="border-b border-text/10 bg-[#2a211a] p-3 lg:hidden">
              <div className="mb-3 flex items-center justify-between gap-3 text-white">
                <h2 className="flex items-center gap-2 font-serif text-lg font-bold">
                  <Presentation className="h-5 w-5" aria-hidden="true" />
                  {activeSlide.deck === 'ktct' ? `Slide KTCT ${activeSlide.num}` : `Slide ${activeSlide.num}`}
                </h2>
                <button
                  type="button"
                  onClick={() => setActiveSlide(null)}
                  className="inline-flex min-h-10 min-w-10 items-center justify-center rounded-xl border border-white/15 bg-white/10 text-white transition-[background-color,transform] duration-150 hover:bg-white/15 active:scale-[0.98] focus-ring"
                  aria-label="Đóng slide nguồn"
                >
                  <X className="h-5 w-5" aria-hidden="true" />
                </button>
              </div>
              <img
                src={`${activeSlide.deck === 'ktct' ? '/slides_ktct' : '/slides'}/slide_${activeSlide.num}.jpg`}
                alt={`Slide nguồn ${activeSlide.num}`}
                className="max-h-72 w-full rounded-xl object-contain shadow-paper"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300' fill='none'%3E%3Crect width='400' height='300' fill='%23f1eadf'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='16' fill='%236F6259'%3EHình ảnh slide chưa cập nhật%3C/text%3E%3C/svg%3E";
                }}
              />
            </div>
          )}

          <div className="flex-1 overflow-y-auto px-4 py-5 md:px-6" aria-live="polite">
            {messages.length === 1 && (
              <div className="mb-6 rounded-2xl border border-text/10 bg-white/60 p-4 md:p-5">
                <div className="flex items-start gap-3">
                  <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <MessageCircle className="h-5 w-5" aria-hidden="true" />
                  </span>
                  <div>
                    <h3 className="font-serif text-xl font-bold">Bắt đầu bằng một câu hỏi cụ thể</h3>
                    <p className="body-pretty mt-1 text-sm leading-6 text-muted">
                      Lily trả lời tốt nhất khi bạn hỏi về khái niệm, ví dụ, so sánh hoặc yêu cầu chỉ ra slide nguồn.
                    </p>
                  </div>
                </div>
                <div className="mt-4 grid gap-2 md:grid-cols-3">
                  {quickPrompts.map(({ icon: Icon, label, prompt }) => (
                    <button
                      key={label}
                      type="button"
                      onClick={() => choosePrompt(prompt)}
                      className="rounded-xl border border-text/10 bg-paper px-4 py-3 text-left transition-[background-color,border-color,transform] duration-150 hover:-translate-y-0.5 hover:border-primary/30 hover:bg-primary/5 focus-ring"
                    >
                      <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
                      <span className="mt-3 block text-sm font-bold">{label}</span>
                      <span className="mt-1 block text-xs leading-5 text-muted">{prompt}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-5">
              {messages.map((msg, idx) => {
                // Collect citations from both decks, de-duplicated by deck+number
                const slideMatches = msg.text.match(/\[Slide\s*(?:KTCT\s*)?\d+\]/gi) || []
                const seen = new Set()
                const citedSlides = []
                for (const m of slideMatches) {
                  const deck = /KTCT/i.test(m) ? 'ktct' : 'mln111'
                  const num = m.replace(/[^0-9]/g, '')
                  const key = `${deck}-${num}`
                  if (!seen.has(key)) {
                    seen.add(key)
                    citedSlides.push({ deck, num })
                  }
                }
                  
                return (
                  <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl shadow-soft ${msg.role === 'user' ? 'bg-cta text-white' : 'bg-primary text-white'}`}>
                      {msg.role === 'user' ? <User className="h-5 w-5" aria-hidden="true" /> : <Bot className="h-5 w-5" aria-hidden="true" />}
                    </div>
                    <article className={`max-w-[86%] rounded-2xl border p-4 shadow-soft ${msg.role === 'user' ? 'rounded-tr-sm border-cta/20 bg-cta/5' : 'rounded-tl-sm border-text/10 bg-paper'}`}>
                      <p className="whitespace-pre-wrap text-base leading-7 text-text">{msg.text}</p>
                      {citedSlides.length > 0 && (
                        <div className="mt-4 border-t border-text/10 pt-4">
                          <p className="mb-3 flex items-center gap-2 text-sm font-bold text-primary">
                            <PanelLeft className="h-4 w-4" aria-hidden="true" />
                            Nguồn tham khảo
                          </p>
                          <div className="flex flex-wrap gap-3">
                            {citedSlides.map(slide => {
                              const isActive = activeSlide && activeSlide.deck === slide.deck && activeSlide.num === slide.num
                              const label = slide.deck === 'ktct' ? `Slide KTCT ${slide.num}` : `Slide ${slide.num}`
                              const imgDir = slide.deck === 'ktct' ? '/slides_ktct' : '/slides'
                              return (
                                <button
                                  key={`${slide.deck}-${slide.num}`}
                                  type="button"
                                  onClick={() => setActiveSlide(slide)}
                                  aria-label={`Mở ${label}`}
                                  className={`w-28 overflow-hidden rounded-xl border bg-white text-left shadow-soft transition-[border-color,box-shadow,transform] duration-150 hover:-translate-y-0.5 focus-ring ${isActive ? 'border-cta shadow-paper' : 'border-text/10 hover:border-primary/30'}`}
                                >
                                  <img src={`${imgDir}/slide_${slide.num}.jpg`} alt={label} className="h-16 w-full object-cover" onError={(e) => { e.target.onerror = null; e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300' fill='none'%3E%3Crect width='400' height='300' fill='%23f1eadf'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='12' fill='%236F6259'%3ETrống%3C/text%3E%3C/svg%3E"; }} />
                                  <span className={`block px-2 py-1.5 text-center text-xs font-semibold ${isActive ? 'bg-cta text-white' : 'text-text'}`}>
                                    {label}
                                  </span>
                                </button>
                              )
                            })}
                          </div>
                        </div>
                      )}
                    </article>
                  </div>
                )
              })}
              
              {isLoading && (
                <div className="flex gap-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary text-white shadow-soft">
                    <Bot className="h-5 w-5" aria-hidden="true" />
                  </div>
                  <div className="flex items-center gap-3 rounded-2xl rounded-tl-sm border border-text/10 bg-paper p-4 text-muted shadow-soft">
                    <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
                    Lily đang suy nghĩ...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          <div className="border-t border-text/10 bg-paper p-4">
            <form onSubmit={e => { e.preventDefault(); handleSend(); }} className="flex gap-3" aria-label="Gửi câu hỏi cho Lily">
              <label htmlFor="chat-input" className="sr-only">Câu hỏi cho Lily</label>
              <div className="relative flex-1">
                <input
                  id="chat-input"
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder="Hỏi Lily về một khái niệm, ví dụ hoặc slide..."
                  className="w-full rounded-xl border border-text/15 bg-white px-4 py-3 pr-11 text-base text-text shadow-soft transition-[border-color,box-shadow] duration-150 placeholder:text-muted/60 focus:border-primary focus:outline-none focus:ring-4 focus:ring-primary/10"
                  disabled={isLoading}
                />
                <Sparkles className="pointer-events-none absolute right-4 top-1/2 h-5 w-5 -translate-y-1/2 text-secondary/60" aria-hidden="true" />
              </div>
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="clay-btn bg-cta border-cta px-4 hover:bg-cta/95 disabled:cursor-not-allowed disabled:opacity-50 md:px-6"
                aria-label="Gửi câu hỏi"
              >
                <Send className="h-5 w-5" aria-hidden="true" />
                <span className="hidden md:inline">Gửi</span>
              </button>
            </form>
          </div>
        </section>

        <aside className="hidden min-h-0 lg:flex lg:flex-col">
          {activeSlide ? (
            <div className="study-panel flex min-h-0 flex-1 flex-col overflow-hidden">
              <div className="flex items-center justify-between gap-3 border-b border-text/10 bg-paper px-4 py-3">
                <h2 className="flex items-center gap-2 font-serif text-lg font-bold text-text">
                  <Presentation className="h-5 w-5 text-primary" aria-hidden="true" />
                  {activeSlide.deck === 'ktct' ? `Slide KTCT ${activeSlide.num}` : `Slide ${activeSlide.num}`}
                </h2>
                <button
                  type="button"
                  onClick={() => setActiveSlide(null)}
                  className="icon-button"
                  aria-label="Đóng slide nguồn"
                >
                  <X className="h-5 w-5" aria-hidden="true" />
                </button>
              </div>
              <div className="flex min-h-0 flex-1 items-center justify-center bg-[#2a211a] p-4">
                <img
                  src={`${activeSlide.deck === 'ktct' ? '/slides_ktct' : '/slides'}/slide_${activeSlide.num}.jpg`}
                  alt={`Slide nguồn ${activeSlide.num}`}
                  className="max-h-full max-w-full rounded-xl object-contain shadow-paper"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300' fill='none'%3E%3Crect width='400' height='300' fill='%232a211a'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='16' fill='%238c8279'%3EHình ảnh slide chưa cập nhật%3C/text%3E%3C/svg%3E";
                  }}
                />
              </div>
            </div>
          ) : (
            <div className="study-panel p-5">
              <p className="eyebrow">Nguồn học liệu</p>
              <h2 className="mt-2 font-serif text-2xl font-bold">Slide sẽ mở ở đây khi câu trả lời có trích dẫn.</h2>
              <p className="body-pretty mt-3 leading-7 text-muted">
                Hãy yêu cầu Lily chỉ ra slide nguồn, hoặc hỏi theo số slide để giữ việc học bám vào tài liệu.
              </p>
              <div className="mt-5 rounded-2xl border border-text/10 bg-white/60 p-4 text-sm leading-6 text-muted">
                Gợi ý: “Dựa trên slide, giải thích vì sao đấu tranh giữa các mặt đối lập là động lực phát triển.”
              </div>
            </div>
          )}
        </aside>
      </main>
    </div>
  )
}

export default ChatPage
