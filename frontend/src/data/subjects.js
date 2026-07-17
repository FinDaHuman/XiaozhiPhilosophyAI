// Single source of truth for the two study subjects: lessons, quiz data,
// slide image locations, and quiz progress groups.
import quizMln111 from './quiz.json'
import quizKtct from './quiz_ktct.json'

export const DEFAULT_SUBJECT = 'mln111'

export const SUBJECTS = {
  mln111: {
    id: 'mln111',
    badge: 'MLN111',
    name: 'Triết học Mác-Lênin',
    topic: 'Chủ đề 4 — Quy luật mâu thuẫn',
    tagline: 'Đi từ khái niệm mặt đối lập đến vận dụng phương pháp luận.',
    slideDir: '/slides',
    slideCount: 33,
    quiz: quizMln111,
    quizGroups: [
      { label: 'Nền tảng', from: 1, to: 10 },
      { label: 'Thống nhất', from: 11, to: 18 },
      { label: 'Đấu tranh', from: 19, to: 26 },
      { label: 'Phân loại', from: 27, to: 34 },
      { label: 'Phương pháp', from: 35, to: 40 },
    ],
    lessons: {
      '1': {
        title: 'Bài 1: Giới thiệu',
        shortTitle: 'Giới thiệu',
        summary: 'Đặt nền tảng cho quy luật mâu thuẫn trong phép biện chứng duy vật.',
        concepts: ['Quy luật', 'Mâu thuẫn', 'Nguồn gốc phát triển'],
        slides: [4, 5, 6],
      },
      '2': {
        title: 'Bài 2: Sự đấu tranh của các mặt đối lập',
        shortTitle: 'Mặt đối lập',
        summary: 'Làm rõ sự thống nhất, đấu tranh và chuyển hóa giữa các mặt đối lập.',
        concepts: ['Mặt đối lập', 'Thống nhất', 'Đấu tranh'],
        slides: [8, 9, 10, 12],
      },
      '3': {
        title: 'Bài 3: Phân loại mâu thuẫn',
        shortTitle: 'Phân loại mâu thuẫn',
        summary: 'Phân biệt mâu thuẫn cơ bản, chủ yếu, bên trong, bên ngoài, đối kháng và không đối kháng.',
        concepts: ['Cơ bản', 'Chủ yếu', 'Bên trong', 'Đối kháng'],
        slides: [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
      },
      '4': {
        title: 'Bài 4: Bản chất quy luật và ý nghĩa phương pháp luận',
        shortTitle: 'Phương pháp luận',
        summary: 'Chuyển từ nắm khái niệm sang cách nhận diện, phân tích và giải quyết mâu thuẫn.',
        concepts: ['Phân tích cụ thể', 'Điều kiện khách quan', 'Vận dụng'],
        slides: [25, 26, 27, 28, 29, 30],
      },
    },
  },

  ktct: {
    id: 'ktct',
    badge: 'MLN122',
    name: 'Kinh tế chính trị Mác-Lênin',
    topic: 'Chủ đề 4 — Cạnh tranh và Độc quyền',
    tagline: 'Từ lý luận độc quyền của Lênin đến biểu hiện mới của chủ nghĩa tư bản ngày nay.',
    slideDir: '/slides_ktct',
    slideCount: 31,
    quiz: quizKtct,
    quizGroups: [
      { label: 'Đặc điểm độc quyền', from: 1, to: 22 },
      { label: 'Độc quyền nhà nước', from: 23, to: 35 },
      { label: 'Biểu hiện mới', from: 36, to: 49 },
      { label: 'ĐQNN ngày nay', from: 50, to: 53 },
      { label: 'Vai trò CNTB', from: 54, to: 60 },
    ],
    lessons: {
      '1': {
        title: 'Bài 1: Lý luận của Lênin về đặc điểm kinh tế của độc quyền',
        shortTitle: 'Đặc điểm độc quyền',
        summary: 'Năm đặc điểm kinh tế cơ bản của độc quyền: tích tụ sản xuất, tư bản tài chính, xuất khẩu tư bản, phân chia thị trường và phân chia lãnh thổ.',
        concepts: ['Tích tụ & tập trung', 'Tư bản tài chính', 'Xuất khẩu tư bản', 'Phân chia thế giới'],
        slides: [3, 4, 5, 6, 7, 8],
      },
      '2': {
        title: 'Bài 2: Độc quyền nhà nước trong chủ nghĩa tư bản',
        shortTitle: 'Độc quyền nhà nước',
        summary: 'Bản chất liên minh giữa tổ chức độc quyền và nhà nước: kết hợp nhân sự, sở hữu nhà nước và hệ thống điều tiết kinh tế.',
        concepts: ['Kết hợp nhân sự', 'Sở hữu nhà nước', 'Điều tiết kinh tế'],
        slides: [9, 10, 11, 12, 13, 14, 15],
      },
      '3': {
        title: 'Bài 3: Biểu hiện mới của độc quyền trong điều kiện ngày nay',
        shortTitle: 'Biểu hiện mới',
        summary: 'Năm biểu hiện mới: công ty xuyên quốc gia, tư bản tài chính đa ngành, dòng vốn mới, toàn cầu hóa và "biên giới mềm".',
        concepts: ['Công ty xuyên quốc gia', 'Toàn cầu hóa', 'Biên giới mềm'],
        slides: [16, 17, 18, 19, 20, 21],
      },
      '4': {
        title: 'Bài 4: Độc quyền nhà nước ngày nay và vai trò lịch sử của CNTB',
        shortTitle: 'Vai trò lịch sử CNTB',
        summary: 'Biểu hiện mới của độc quyền nhà nước, vai trò tích cực của chủ nghĩa tư bản và những giới hạn lịch sử của nó.',
        concepts: ['Cơ chế nhân sự mới', 'Vai trò tích cực', 'Giới hạn lịch sử'],
        slides: [22, 23, 24, 25, 26, 27, 28, 29, 30],
      },
    },
  },
}

export const SUBJECT_ORDER = ['mln111', 'ktct']

export function getSubject(subjectId) {
  return SUBJECTS[subjectId] || SUBJECTS[DEFAULT_SUBJECT]
}
