import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { Send } from 'lucide-react'
import { JarvisOrb } from 'jarvis-ai-web-animation'
import { apiFetch } from '../config'
import './HiroPage.css'

const ASSISTANTS = {
  lily: {
    name: 'Lily',
    accent: '#9b6cff',
    endpoint: '/chat',
    placeholder: 'Hỏi Lily về bài học...',
    palette: {
      core: 0xf4eaff,
      primary: 0xa855f7,
      secondary: 0x7c3aed,
      tertiary: 0xc084fc,
      deep: 0x2e1065,
      fallback: 'radial-gradient(circle, #f4eaff 0%, #a855f7 30%, #2e1065 72%, transparent)',
    },
  },
  hiro: {
    name: 'Hiro',
    accent: '#00e7f2',
    endpoint: '/chat/hiro',
    placeholder: 'Hỏi Hiro bất kỳ điều gì...',
    palette: 'cyan',
  },
}

const ASSISTANT_TITLES = {
  lily: 'Language Integrated Learning Yield',
  hiro: 'Hyper-scaled Investment & Risk Oversight',
}

const TITLE_DELETE_DELAY = 18
const TITLE_TYPE_DELAY = 25
const TITLE_PHASE_PAUSE = 80

function buildHistory(turns) {
  return turns
    .filter(turn => turn.answer && !turn.failed)
    .slice(-5)
    .map(turn => ({ question: turn.question, answer: turn.answer }))
}

function cleanModelText(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/^\s*[-*]\s+/gm, '• ')
    .trim()
}

function ModelMark({ accent }) {
  return (
    <span className="hiro-model-mark" style={{ '--model-accent': accent }} aria-hidden="true">
      <span />
    </span>
  )
}

function HiroPage() {
  const [selected, setSelected] = useState('hiro')
  const [threads, setThreads] = useState({ lily: [], hiro: [] })
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [orbState, setOrbState] = useState('idle')
  const [expandedTitles, setExpandedTitles] = useState({ lily: false, hiro: false })
  const [displayedTitles, setDisplayedTitles] = useState({ lily: 'Lily', hiro: 'Hiro' })
  const [typingTitles, setTypingTitles] = useState({ lily: false, hiro: false })
  const inputRef = useRef(null)
  const transcriptRef = useRef(null)
  const shouldStickToBottomRef = useRef(true)
  const forceScrollToBottomRef = useRef(false)
  const titleTimersRef = useRef({})
  const displayedTitlesRef = useRef({ lily: 'Lily', hiro: 'Hiro' })

  const assistant = ASSISTANTS[selected]
  const turns = threads[selected]
  const hasConversation = turns.length > 0
  const orbSize = hasConversation ? 'panel' : 'hero'
  const ariaStatus = isLoading ? `${assistant.name} đang suy nghĩ` : `${assistant.name} sẵn sàng`

  const visibleTurns = useMemo(
    () => turns.map(turn => ({ ...turn, answer: cleanModelText(turn.answer || '') })),
    [turns],
  )

  useEffect(() => () => {
    Object.values(titleTimersRef.current).forEach(window.clearTimeout)
  }, [])

  useLayoutEffect(() => {
    const transcript = transcriptRef.current
    if (!transcript) return

    if (forceScrollToBottomRef.current || shouldStickToBottomRef.current) {
      transcript.scrollTop = transcript.scrollHeight
      shouldStickToBottomRef.current = true
      forceScrollToBottomRef.current = false
    }
  }, [selected, visibleTurns])

  const handleTranscriptScroll = (event) => {
    const transcript = event.currentTarget
    const distanceFromBottom = transcript.scrollHeight - transcript.scrollTop - transcript.clientHeight
    shouldStickToBottomRef.current = distanceFromBottom <= 64
  }

  const chooseAssistant = (id) => {
    if (isLoading || id === selected) return
    forceScrollToBottomRef.current = true
    setSelected(id)
    setInput('')
    setOrbState('idle')
    window.requestAnimationFrame(() => inputRef.current?.focus())
  }

  const updateDisplayedTitle = (id, value) => {
    displayedTitlesRef.current[id] = value
    setDisplayedTitles(previous => ({ ...previous, [id]: value }))
  }

  const animateTitle = (id, target) => {
    window.clearTimeout(titleTimersRef.current[id])

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      updateDisplayedTitle(id, target)
      setTypingTitles(previous => ({ ...previous, [id]: false }))
      return
    }

    setTypingTitles(previous => ({ ...previous, [id]: true }))

    const typeNextCharacter = (characterIndex = 0) => {
      if (characterIndex >= target.length) {
        setTypingTitles(previous => ({ ...previous, [id]: false }))
        return
      }

      updateDisplayedTitle(id, target.slice(0, characterIndex + 1))
      titleTimersRef.current[id] = window.setTimeout(
        () => typeNextCharacter(characterIndex + 1),
        TITLE_TYPE_DELAY,
      )
    }

    const deleteNextCharacter = () => {
      const current = displayedTitlesRef.current[id]
      if (!current) {
        titleTimersRef.current[id] = window.setTimeout(() => typeNextCharacter(), TITLE_PHASE_PAUSE)
        return
      }

      updateDisplayedTitle(id, current.slice(0, -1))
      titleTimersRef.current[id] = window.setTimeout(deleteNextCharacter, TITLE_DELETE_DELAY)
    }

    deleteNextCharacter()
  }

  const toggleAssistantTitle = () => {
    if (hasConversation) return

    const nextExpanded = !expandedTitles[selected]
    const target = nextExpanded ? ASSISTANT_TITLES[selected] : assistant.name
    setExpandedTitles(previous => ({ ...previous, [selected]: nextExpanded }))
    animateTitle(selected, target)
  }

  const submit = async (event) => {
    event.preventDefault()
    const question = input.trim()
    if (!question || isLoading) return

    const activeAssistant = selected
    const history = buildHistory(threads[activeAssistant])
    forceScrollToBottomRef.current = true
    setInput('')
    setIsLoading(true)
    setOrbState('thinking')
    setThreads(previous => ({
      ...previous,
      [activeAssistant]: [...previous[activeAssistant], { question, answer: '', failed: false }],
    }))

    try {
      const response = await apiFetch(ASSISTANTS[activeAssistant].endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: question, history }),
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data = await response.json()
      if (!data.answer?.trim()) throw new Error('Empty response')

      setThreads(previous => {
        const next = [...previous[activeAssistant]]
        next[next.length - 1] = { question, answer: data.answer.trim(), failed: false }
        return { ...previous, [activeAssistant]: next }
      })
      setOrbState('success')
    } catch (error) {
      console.error(`${ASSISTANTS[activeAssistant].name} request failed:`, error)
      setThreads(previous => {
        const next = [...previous[activeAssistant]]
        next[next.length - 1] = {
          question,
          answer: `Không thể kết nối với ${ASSISTANTS[activeAssistant].name}. Vui lòng thử lại.`,
          failed: true,
        }
        return { ...previous, [activeAssistant]: next }
      })
      setOrbState('alert')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="hiro-page">
      <header className="hiro-header">
        <Link to="/" className="hiro-brand">Lily</Link>
        <nav aria-label="Điều hướng chính">
          <a href="/#study">Bài học</a>
          <Link to="/chat">Chat</Link>
          <Link to="/quiz">Ôn tập</Link>
          <Link to="/hiro" className="is-current" aria-current="page">Hiro</Link>
        </nav>
      </header>

      <main className={`hiro-stage ${hasConversation ? 'has-conversation' : ''}`}>
        <div className="hiro-model-selector" aria-label="Chọn trợ lý AI">
          {Object.entries(ASSISTANTS).map(([id, model]) => (
            <button
              key={id}
              type="button"
              className={selected === id ? 'is-selected' : ''}
              style={{ '--model-accent': model.accent }}
              aria-pressed={selected === id}
              disabled={isLoading}
              onClick={() => chooseAssistant(id)}
            >
              <ModelMark accent={model.accent} />
              {model.name}
            </button>
          ))}
        </div>

        <div className="hiro-workspace">
          <section className="hiro-orb-region" aria-label={ariaStatus}>
            {!hasConversation && (
              <h1 className={expandedTitles[selected] ? 'is-expanded' : ''}>
                <span>{displayedTitles[selected]}</span>
                <i className={typingTitles[selected] ? 'is-visible' : ''} aria-hidden="true" />
              </h1>
            )}
            <button
              type="button"
              className="hiro-orb-shell"
              onClick={toggleAssistantTitle}
              aria-label={hasConversation ? ariaStatus : `Chuyển đổi tên đầy đủ của ${assistant.name}`}
              aria-disabled={hasConversation}
              tabIndex={hasConversation ? -1 : 0}
            >
              <JarvisOrb
                key={selected}
                size={orbSize}
                state={orbState}
                palette={assistant.palette}
                quality="auto"
                interactive={!hasConversation}
                breathing
                breathingIntensity={0.75}
                ariaLabel={ariaStatus}
              />
            </button>
          </section>

          {hasConversation && (
            <section
              ref={transcriptRef}
              className="hiro-transcript"
              aria-label={`Cuộc trò chuyện với ${assistant.name}`}
              aria-live="polite"
              onScroll={handleTranscriptScroll}
            >
              {visibleTurns.map((turn, index) => (
                <article className="hiro-turn" key={`${turn.question}-${index}`}>
                  <div className="hiro-question">
                    <h2>Bạn</h2>
                    <p>{turn.question}</p>
                  </div>
                  <div className={`hiro-answer ${turn.failed ? 'is-error' : ''}`}>
                    <h2>{assistant.name}</h2>
                    {turn.answer ? (
                      <p>{turn.answer}</p>
                    ) : (
                      <span className="hiro-thinking" role="status" aria-label={`${assistant.name} đang suy nghĩ`}>
                        <i /><i /><i />
                      </span>
                    )}
                  </div>
                </article>
              ))}
            </section>
          )}
        </div>

        <form className="hiro-composer" onSubmit={submit}>
          <label htmlFor="hiro-input" className="sr-only">Câu hỏi cho {assistant.name}</label>
          <input
            ref={inputRef}
            id="hiro-input"
            value={input}
            onChange={event => setInput(event.target.value)}
            placeholder={hasConversation ? `Hỏi tiếp ${assistant.name}...` : assistant.placeholder}
            disabled={isLoading}
            maxLength={2000}
            autoComplete="off"
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            <Send aria-hidden="true" />
            <span>Gửi</span>
          </button>
        </form>
      </main>
    </div>
  )
}

export default HiroPage
