import { useMemo, useRef, useState } from 'react'
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
  const inputRef = useRef(null)

  const assistant = ASSISTANTS[selected]
  const turns = threads[selected]
  const hasConversation = turns.length > 0
  const orbSize = hasConversation ? 'panel' : 'hero'
  const ariaStatus = isLoading ? `${assistant.name} đang suy nghĩ` : `${assistant.name} sẵn sàng`

  const visibleTurns = useMemo(
    () => turns.map(turn => ({ ...turn, answer: cleanModelText(turn.answer || '') })),
    [turns],
  )

  const chooseAssistant = (id) => {
    if (isLoading || id === selected) return
    setSelected(id)
    setInput('')
    setOrbState('idle')
    window.requestAnimationFrame(() => inputRef.current?.focus())
  }

  const submit = async (event) => {
    event.preventDefault()
    const question = input.trim()
    if (!question || isLoading) return

    const activeAssistant = selected
    const history = buildHistory(threads[activeAssistant])
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
            {!hasConversation && <h1>{assistant.name}</h1>}
            <div className="hiro-orb-shell">
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
            </div>
          </section>

          {hasConversation && (
            <section className="hiro-transcript" aria-label={`Cuộc trò chuyện với ${assistant.name}`} aria-live="polite">
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
