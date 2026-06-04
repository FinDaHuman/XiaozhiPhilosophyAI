import React, { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, Send, Bot, User, Loader2, Sparkles, X, Presentation } from 'lucide-react'

const ChatPage = () => {
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Xin chào, tôi là XiaoZhi - trợ lý AI triết học của bạn. Bạn muốn khám phá điều gì hôm nay?' }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [activeSlide, setActiveSlide] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: userMessage }])
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      })
      
      if (response.ok) {
        const data = await response.json()
        setMessages(prev => [...prev, { role: 'ai', text: data.answer }])
        
        // Auto-detect slide to show
        const slideMatches = data.answer.match(/\[Slide\s*(\d+)\]/gi)
        if (slideMatches) {
          const firstSlide = slideMatches[0].replace(/[^0-9]/g, '')
          setActiveSlide(firstSlide)
        }
      } else {
        setMessages(prev => [...prev, { role: 'ai', text: 'Xin lỗi, tôi gặp lỗi kết nối. Vui lòng thử lại sau.' }])
      }
    } catch (error) {
      console.error(error)
      setMessages(prev => [...prev, { role: 'ai', text: 'Không thể kết nối với máy chủ XiaoZhi. Vui lòng kiểm tra lại.' }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col h-screen">
      <div className="bg-white shadow-sm sticky top-0 z-40 border-b-2 border-secondary/20 flex-shrink-0">
        <div className="w-full px-4 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center text-primary font-bold hover:opacity-80 transition-opacity">
            <ArrowLeft className="w-5 h-5 mr-1" />
            Trang chủ
          </Link>
          <h1 className="text-xl md:text-2xl font-bold text-text flex items-center gap-2">
            <Bot className="text-primary w-6 h-6" />
            XiaoZhi AI
          </h1>
          <div className="w-24"></div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden p-4 md:p-6 flex flex-col lg:flex-row gap-6 max-w-[1800px] mx-auto w-full transition-all duration-500">
        {/* LEFT PANEL - SLIDE VIEWER */}
        {activeSlide && (
          <div className="flex w-full lg:w-2/3 h-[40vh] lg:h-full bg-white/50 backdrop-blur-sm rounded-2xl border-2 border-secondary/20 shadow-clay flex-col overflow-hidden transition-all duration-500 opacity-100">
            <div className="bg-white border-b-2 border-secondary/20 p-2 md:p-4 flex items-center justify-between shrink-0">
              <h2 className="text-base md:text-lg font-bold text-primary flex items-center gap-2">
                <Presentation className="w-4 h-4 md:w-5 md:h-5" /> Nguồn trích dẫn: Slide {activeSlide}
              </h2>
              <button 
                onClick={() => setActiveSlide(null)}
                className="p-1.5 md:p-2 hover:bg-secondary/10 rounded-full text-text/60 hover:text-text transition-colors"
                title="Đóng slide"
              >
                <X className="w-4 h-4 md:w-5 md:h-5" />
              </button>
            </div>
            <div className="flex-1 p-4 md:p-6 flex items-center justify-center bg-secondary/5 min-h-0">
              <img 
                src={`/slides/slide_${activeSlide}.jpg`} 
                alt={`Slide ${activeSlide}`} 
                className="max-w-full max-h-full object-contain rounded-xl shadow-lg border-2 border-secondary/10" 
              />
            </div>
          </div>
        )}

        {/* RIGHT PANEL - CHAT */}
        <div className={`w-full ${activeSlide ? 'lg:w-1/3' : 'max-w-4xl mx-auto'} bg-white/50 backdrop-blur-sm rounded-2xl border-2 border-secondary/20 shadow-clay flex flex-col h-full overflow-hidden transition-all duration-500`}>
          
          <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
            {messages.map((msg, idx) => {
              const slideMatches = msg.text.match(/\[Slide\s*(\d+)\]/gi);
              const citedSlides = slideMatches 
                ? [...new Set(slideMatches.map(m => m.replace(/[^0-9]/g, '')))]
                : [];
                
              return (
                <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm ${msg.role === 'user' ? 'bg-cta text-white' : 'bg-primary text-white'}`}>
                    {msg.role === 'user' ? <User className="w-6 h-6" /> : <Bot className="w-6 h-6" />}
                  </div>
                  <div className={`max-w-[85%] p-4 rounded-2xl shadow-sm border-2 ${msg.role === 'user' ? 'bg-white border-cta/20 rounded-tr-sm' : 'bg-white border-secondary/20 rounded-tl-sm'}`}>
                    <p className="text-base text-text leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                    {citedSlides.length > 0 && (
                      <div className="mt-4 pt-4 border-t-2 border-secondary/10">
                        <p className="text-sm font-bold text-primary mb-2 flex items-center gap-2">
                          <Sparkles className="w-4 h-4" /> Nguồn tham khảo:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {citedSlides.map(slide => (
                            <button 
                              key={slide} 
                              onClick={() => setActiveSlide(slide)}
                              className={`block w-24 md:w-32 overflow-hidden rounded-lg border-2 transition-all text-left ${activeSlide === slide ? 'border-cta ring-2 ring-cta/30' : 'border-primary/20 hover:border-primary'}`}
                            >
                              <img src={`/slides/slide_${slide}.jpg`} alt={`Slide ${slide}`} className="w-full h-auto object-cover" />
                              <div className={`text-center text-xs font-semibold py-1 ${activeSlide === slide ? 'bg-cta text-white' : 'bg-primary/5 text-text'}`}>
                                Xem Slide {slide}
                              </div>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
            
            {isLoading && (
              <div className="flex gap-3">
                <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm bg-primary text-white">
                  <Bot className="w-6 h-6" />
                </div>
                <div className="bg-white p-4 rounded-2xl border-2 border-secondary/20 rounded-tl-sm shadow-sm flex items-center gap-3 text-text/60">
                  <Loader2 className="w-5 h-5 animate-spin" /> XiaoZhi đang suy nghĩ...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 bg-white border-t-2 border-secondary/20 shrink-0">
            <form onSubmit={e => { e.preventDefault(); handleSend(); }} className="flex gap-3">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder="Hỏi XiaoZhi..."
                  className="w-full px-5 py-3 pr-12 rounded-xl border-2 border-secondary/30 focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/10 transition-all bg-background/50 text-text text-lg"
                  disabled={isLoading}
                />
                <Sparkles className="absolute right-4 top-1/2 -translate-y-1/2 text-secondary/50 w-5 h-5 pointer-events-none" />
              </div>
              <button 
                type="submit" 
                disabled={isLoading || !input.trim()}
                className="clay-btn !px-4 md:!px-6 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-lg"
              >
                <Send className="w-5 h-5" />
                <span className="hidden md:inline">Gửi</span>
              </button>
            </form>
          </div>

        </div>
      </div>
    </div>
  )
}

export default ChatPage
