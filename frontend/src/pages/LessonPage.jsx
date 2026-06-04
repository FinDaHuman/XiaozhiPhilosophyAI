import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, ArrowRight } from 'lucide-react'

const lessonData = {
  "1": {
    title: "Bài 1: Giới thiệu",
    slides: [4, 5, 6]
  },
  "2": {
    title: "Bài 2: Sự đấu tranh của các mặt đối lập",
    slides: [8, 9, 10, 12]
  },
  "3": {
    title: "Bài 3: Phân loại mâu thuẫn",
    slides: [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
  },
  "4": {
    title: "Bài 4: Bản chất quy luật và ý nghĩa phương pháp luận",
    slides: [25, 26, 27, 28, 29, 30]
  }
}

const LessonPage = () => {
  const { id } = useParams()
  const lesson = lessonData[id]

  if (!lesson) {
    return <div className="p-8 text-center"><p>Lesson not found.</p><Link to="/">Go Home</Link></div>
  }

  const prevId = parseInt(id) > 1 ? (parseInt(id) - 1).toString() : null
  const nextId = parseInt(id) < 4 ? (parseInt(id) + 1).toString() : null

  return (
    <div className="min-h-screen bg-background pb-20">
      <div className="bg-white shadow-sm sticky top-0 z-40 border-b-2 border-secondary/20">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center text-primary font-bold hover:opacity-80 transition-opacity">
            <ArrowLeft className="w-5 h-5 mr-1" />
            Trang chủ
          </Link>
          <h1 className="text-xl md:text-2xl font-bold text-text truncate max-w-[60%]">{lesson.title}</h1>
          <div className="flex gap-2">
            {prevId ? (
              <Link to={`/lesson/${prevId}`} className="p-2 bg-secondary/10 rounded-lg text-primary hover:bg-secondary/20 transition-colors">
                <ArrowLeft className="w-5 h-5" />
              </Link>
            ) : <div className="w-9"></div>}
            {nextId ? (
              <Link to={`/lesson/${nextId}`} className="p-2 bg-secondary/10 rounded-lg text-primary hover:bg-secondary/20 transition-colors">
                <ArrowRight className="w-5 h-5" />
              </Link>
            ) : <div className="w-9"></div>}
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
        {lesson.slides.map((slideNum) => (
          <div key={slideNum} className="clay-card overflow-hidden">
            <img 
              src={`/slides/slide_${slideNum}.jpg`} 
              alt={`Slide ${slideNum}`} 
              className="w-full h-auto"
              loading="lazy"
            />
          </div>
        ))}
      </div>
    </div>
  )
}

export default LessonPage
