import React from 'react'
import { Link } from 'react-router-dom'
import { BookOpen, HelpCircle, Bot, Sparkles, ArrowRight } from 'lucide-react'

const LandingPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center relative bg-cover bg-center overflow-x-hidden" style={{ backgroundImage: "url('/images/bg.jpg')" }}>
      {/* Overlay for readability */}
      <div className="absolute inset-0 bg-white/60 backdrop-blur-sm z-0"></div>
      
      <div className="relative z-10 w-full max-w-6xl p-4 md:p-8 flex flex-col items-center justify-center min-h-screen my-8">
        
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto mb-16 animate-in slide-in-from-bottom-5 duration-700 fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary font-bold mb-6 border-2 border-primary/20">
            <Sparkles className="w-5 h-5" />
            <span>Tương Lai Của Việc Khám Phá Triết Học</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-black text-text mb-6 leading-tight">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">XiaoZhi</span>
          </h1>
          <p className="text-xl md:text-2xl text-text/80 font-medium mb-10 leading-relaxed">
            Triết gia AI cá nhân của bạn. Cùng khám phá sâu các lý thuyết phức tạp và tìm hiểu triết học Mác - Lênin qua các cuộc trò chuyện tương tác đầy thú vị.
          </p>
          <Link to="/chat" className="inline-flex items-center gap-3 bg-primary text-white text-xl font-bold px-8 py-4 rounded-2xl shadow-clay hover:-translate-y-1 hover:shadow-lg transition-all duration-300 border-4 border-white/20 active:translate-y-0">
            <Bot className="w-7 h-7" />
            Trò Chuyện Cùng XiaoZhi Ngay
          </Link>
        </div>

        {/* Feature Grid */}
        <div className="grid md:grid-cols-2 gap-8 w-full">
          
          {/* Lessons Card */}
          <div className="clay-card p-8 flex flex-col h-full bg-white/90">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-secondary/20 rounded-xl text-primary">
                <BookOpen className="w-8 h-8" />
              </div>
              <h2 className="text-3xl font-bold text-primary">Bài Học Trọng Tâm</h2>
            </div>
            <p className="text-text/70 text-lg mb-8 flex-1">
              Nắm vững các nguyên lý cơ bản qua các học phần trực quan, được trích xuất trực tiếp từ giáo trình chuẩn.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Link to="/lesson/1" className="flex items-center justify-between p-4 rounded-xl border-2 border-secondary/20 hover:border-primary hover:bg-primary/5 transition-colors group">
                <span className="font-bold text-text group-hover:text-primary">1. Giới thiệu</span>
                <ArrowRight className="w-4 h-4 text-text/40 group-hover:text-primary" />
              </Link>
              <Link to="/lesson/2" className="flex items-center justify-between p-4 rounded-xl border-2 border-secondary/20 hover:border-primary hover:bg-primary/5 transition-colors group">
                <span className="font-bold text-text group-hover:text-primary">2. Mặt đối lập</span>
                <ArrowRight className="w-4 h-4 text-text/40 group-hover:text-primary" />
              </Link>
              <Link to="/lesson/3" className="flex items-center justify-between p-4 rounded-xl border-2 border-secondary/20 hover:border-primary hover:bg-primary/5 transition-colors group">
                <span className="font-bold text-text group-hover:text-primary">3. Phân loại mâu thuẫn</span>
                <ArrowRight className="w-4 h-4 text-text/40 group-hover:text-primary" />
              </Link>
              <Link to="/lesson/4" className="flex items-center justify-between p-4 rounded-xl border-2 border-secondary/20 hover:border-primary hover:bg-primary/5 transition-colors group">
                <span className="font-bold text-text group-hover:text-primary">4. Phương pháp luận</span>
                <ArrowRight className="w-4 h-4 text-text/40 group-hover:text-primary" />
              </Link>
            </div>
          </div>

          {/* Quiz Card */}
          <div className="clay-card p-8 flex flex-col h-full bg-white/90 border-cta/30">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-cta/20 rounded-xl text-cta">
                <HelpCircle className="w-8 h-8" />
              </div>
              <h2 className="text-3xl font-bold text-cta">Kiểm Tra Kiến Thức</h2>
            </div>
            <p className="text-text/70 text-lg mb-8 flex-1">
              Thử thách bản thân với 40 câu hỏi trắc nghiệm tương tác. Nhận phản hồi ngay lập tức để củng cố kiến thức triết học của bạn.
            </p>
            <div className="mt-auto">
              <Link to="/quiz" className="flex items-center justify-center gap-2 w-full bg-cta text-white text-lg font-bold px-6 py-4 rounded-xl shadow-clay hover:-translate-y-1 transition-all duration-300 border-2 border-white/20 active:translate-y-0">
                Bắt Đầu Làm Bài
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}

export default LandingPage
