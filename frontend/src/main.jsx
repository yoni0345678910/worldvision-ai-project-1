import React, { useEffect, useMemo, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { marked } from 'marked'
import {
  Bot, FileAudio, FileText, Heart, History, Menu,
  MessageCircle, Paperclip, Plus, Search, Send, Sparkles, X
} from 'lucide-react'
import './styles.css'

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

async function request(path, options = {}) {
  const startTime = performance.now()

  let response
  try {
    response = await fetch(`${API_BASE}${path}`, options)
  } catch {
    throw new Error('백엔드 서버에 연결할 수 없습니다. API 주소 또는 서버 실행 상태를 확인해 주세요.')
  }

  const elapsedTime = ((performance.now() - startTime) / 1000).toFixed(2)

  let data
  try {
    data = await response.json()
  } catch {
    data = null
  }

  if (!response.ok) {
    const detail = data?.detail
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail.map(item => item?.msg || JSON.stringify(item)).join(', ')
        : detail?.msg || `요청에 실패했습니다. (${response.status})`

    const error = new Error(message)
    error.status = response.status
    throw error
  }

  if (data && typeof data === 'object') {
    data.elapsed_time = Number(elapsedTime)
  }

  return data
}

function sourceLabel(source) {
  if (typeof source === 'string') return source
  return source?.title || source?.filename || source?.source || source?.name || JSON.stringify(source)
}

const navigation = [
  { id: 'search', label: '사내 지식검색', icon: Search },
  { id: 'minutes', label: 'AI 회의록', icon: FileAudio },
  { id: 'report', label: 'AI 보고서', icon: FileText },
]

function Brand() {
  return <div className="brand"><div className="brand-mark"><Heart size={22} fill="currentColor" /></div><div><b>WorldVision</b><span>AI Assistant</span></div></div>
}

function Sidebar({ active, setActive, open, setOpen }) {
  return <aside className={`sidebar ${open ? 'open' : ''}`}>
    <div className="side-head"><Brand /><button className="mobile-close" onClick={() => setOpen(false)}><X /></button></div>
    <button className="new-chat" onClick={() => { setActive('search'); location.reload() }}><Plus size={18} /> 새 대화 시작</button>
    <nav>{navigation.map(({ id, label, icon: Icon }) => <button key={id} className={active === id ? 'active' : ''} onClick={() => { setActive(id); setOpen(false) }}><Icon size={19} />{label}</button>)}</nav>
    <div className="history-title"><History size={16} /> 최근 활동</div>
    <div className="history-empty">아직 저장된 활동이 없습니다.</div>
    <div className="side-footer"><div className="avatar">WV</div><div><b>월드비전 임직원</b><span>업무 지원 공간</span></div></div>
  </aside>
}

function Header({ active, onMenu, apiState }) {
  const item = navigation.find(x => x.id === active)
  const label = apiState === 'connected' ? 'API 연결됨' : apiState === 'checking' ? 'API 확인 중' : 'API 연결 안 됨'
  return <header><button className="menu-button" onClick={onMenu}><Menu /></button><div><h2>{item.label}</h2><p>월드비전의 더 나은 업무를 AI와 함께하세요</p></div><div className={`status ${apiState}`}><i /> {label}</div></header>
}

function Welcome({ onPrompt }) {
  const prompts = ['월드비전의 주요 사업을 알려줘', '아동 후원 업무 절차를 정리해줘', '최근 사업 보고서 내용을 찾아줘']
  return <div className="welcome">
    <div className="hero-icon"><Sparkles size={31} /></div>
    <h1>무엇을 도와드릴까요?</h1>
    <p>사내 자료를 기반으로 필요한 정보를 빠르고 정확하게 찾아드려요.</p>
    <div className="prompt-grid">{prompts.map((p, i) => <button key={p} onClick={() => onPrompt(p)}><span>{['01','02','03'][i]}</span>{p}</button>)}</div>
  </div>
}

function SearchPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const topK = 3
  const sessionId = useMemo(() => crypto.randomUUID(), [])
  const end = useRef(null)
  
  useEffect(() => {
    end.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const submit = async (preset) => {
  const query = (preset || input).trim()
  if (!query || loading) return

  setMessages(v => [...v, { role: 'user', text: query }])
  setInput('')
  setLoading(true)

  try {
    let data

    try {
      data = await request('/api/v1/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          session_id: sessionId,
          embedding_model: 'text-embedding-3-large',
          top_k: topK,
          search_type: 'hybrid',
          filters: null
        })
      })
    } catch (error) {
      if (![405, 422].includes(error.status)) throw error

      const params = new URLSearchParams({
        query,
        top_k: String(topK),
        threshold: '0.7'
      })

      data = await request(`/api/v1/search?${params}`)
    }

    setMessages(v => [
      ...v,
      {
        role: 'ai',
        text: data.answer,
        sources: data.sources,
        elapsedTime: data.elapsed_time
      }
    ])
  } catch (e) {
    setMessages(v => [
      ...v,
      { role: 'error', text: e.message }
    ])
  } finally {
    setLoading(false)
  }
}

  return (
  <section className="chat-page">
    <div className="chat-scroll">
      {!messages.length ? (
        <Welcome onPrompt={submit} />
      ) : (
        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>
              <div className="message-icon">
                {m.role === 'user' ? '나' : <Bot size={18} />}
              </div>

              <div>
                <div className="bubble">
                  {typeof m.text === 'string'
                    ? m.text
                    : JSON.stringify(m.text, null, 2)}
                </div>

                {m.sources?.length > 0 && (
                  <div className="sources">
                    <b>참고 문서</b>
                    {m.sources.map((s, j) => (
                      <span key={j}>
                        <Paperclip size={13} />
                        {sourceLabel(s)}
                      </span>
                    ))}
                  </div>
                )}

                {m.elapsedTime != null && (
                  <div className="response-time">
                    응답 시간: {m.elapsedTime}초
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message ai">
              <div className="message-icon">
                <Bot size={18} />
              </div>
              <div className="bubble typing">
                <i />
                <i />
                <i />
              </div>
            </div>
          )}

          <div ref={end} />
        </div>
      )}
    </div>

    <div className="composer-wrap">
      <div className="composer">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              submit()
            }
          }}
          placeholder="사내 업무에 대해 무엇이든 물어보세요"
          rows="1"
        />

        <div className="composer-actions">
          <span>Enter로 질문 보내기</span>
          <button
            aria-label="질문 보내기"
            onClick={() => submit()}
            disabled={!input.trim() || loading}
          >
            <Send size={18} />
          </button>
        </div>
      </div>

      <small>
        AI 답변은 정확하지 않을 수 있습니다. 중요한 내용은 반드시 확인해 주세요.
      </small>
    </div>
  </section>
)
}

function MinutesPage() {
  const [file, setFile] = useState(null), [result, setResult] = useState(null), [error, setError] = useState(''), [loading, setLoading] = useState(false)
  const submit = async () => { if (!file) return; setLoading(true); setError(''); const form = new FormData(); form.append('file', file); try { setResult(await request('/api/v1/minutes', { method: 'POST', body: form })) } catch(e) { setError(e.message) } finally { setLoading(false) } }
  return <FeaturePage eyebrow="MEETING NOTE" title="회의를 기록하는 가장 쉬운 방법" description="회의 음성 파일을 올리면 내용을 분석해 핵심을 정리합니다.">
    <div className="upload-card"><label className="dropzone"><input type="file" accept=".flac,.m4a,.mp3,.mp4,.mpeg,.mpga,.oga,.ogg,.wav,.webm" onChange={e => { setFile(e.target.files[0]); setResult(null) }}/><div className="upload-icon"><FileAudio /></div><b>{file ? file.name : '회의 음성 파일을 선택하세요'}</b><span>{file ? '다른 파일을 선택하려면 클릭하세요' : 'MP3, M4A, WAV, MP4, WEBM 등 지원'}</span></label><button className="primary" disabled={!file || loading} onClick={submit}>{loading ? '회의록 작성 중...' : 'AI 회의록 만들기'}</button>{error && <div className="error-box">{error}</div>}</div>
    {result && <ResultCard title={result.filename}><h3>회의 요약</h3><p>{result.summary}</p>{result.key_issues?.length > 0 && <><h3>주요 논의사항</h3><ul>{result.key_issues.map(x => <li>{x}</li>)}</ul></>}{result.decisions?.length > 0 && <><h3>결정사항</h3><ul>{result.decisions.map(x => <li>{x}</li>)}</ul></>}
    {result.elapsed_time != null && (
  <div className="response-time">
    응답 시간: {result.elapsed_time}초
  </div>
)}
    </ResultCard>}
  </FeaturePage>
}

function ReportPage() {
  const [topic, setTopic] = useState(''), [report, setReport] = useState(''), [elapsedTime, setElapsedTime] = useState(null), [error, setError] = useState(''), [loading, setLoading] = useState(false)
  const submit = async () => {
  if (!topic.trim()) return

  setLoading(true)
  setError('')

  try {
    let data

    try {
      data = await request('/api/v1/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: topic.trim() })
      })
    } catch (error) {
      if (![415, 422].includes(error.status)) throw error

      const form = new FormData()
      form.append('topic', topic.trim())

      data = await request('/api/v1/report', {
        method: 'POST',
        body: form
      })
    }

    setReport(data.report)
    setElapsedTime(data.elapsed_time)

  } catch (e) {
    setError(e.message)
  } finally {
    setLoading(false)
  }
}
  return <FeaturePage eyebrow="AI BUSINESS REPORT" title="아이디어를 보고서 초안으로" description="주제를 입력하면 개요, 현황 분석, 실행 제언을 갖춘 보고서를 작성합니다.">
    <div className="report-form"><label>보고서 주제</label><textarea value={topic} onChange={e => setTopic(e.target.value)} placeholder="예: 2027년 국내 아동복지 사업 확대 전략"/><div className="topic-examples">추천 주제 <button onClick={() => setTopic('후원자 참여율 향상을 위한 디지털 캠페인 전략')}>디지털 캠페인 전략</button><button onClick={() => setTopic('지역사회 아동 돌봄 사업 개선 방안')}>아동 돌봄 개선</button></div><button className="primary" onClick={submit} disabled={!topic.trim() || loading}>{loading ? '보고서 작성 중...' : '보고서 초안 만들기'}</button>{error && <div className="error-box">{error}</div>}</div>
    {report && <ResultCard title="생성된 보고서"><div className="markdown" dangerouslySetInnerHTML={{__html: marked.parse(report)}} />
    {elapsedTime != null && (
  <div className="response-time">
    응답 시간: {elapsedTime}초
  </div>
)}
    </ResultCard>}
  </FeaturePage>
}

function FeaturePage({ eyebrow, title, description, children }) { return <div className="feature-page"><div className="feature-intro"><span>{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>{children}</div> }
function ResultCard({ title, children }) { return <article className="result-card"><div className="result-head"><FileText size={19}/><b>{title}</b></div><div className="result-body">{children}</div></article> }

function App() {
  const [active, setActive] = useState('search'), [menu, setMenu] = useState(false)
  const [apiState, setApiState] = useState('checking')
  useEffect(() => {
    request('/health').then(() => setApiState('connected')).catch(() => setApiState('disconnected'))
  }, [])
  return <div className="app"><Sidebar active={active} setActive={setActive} open={menu} setOpen={setMenu}/>{menu && <div className="overlay" onClick={() => setMenu(false)}/>}<main><Header active={active} onMenu={() => setMenu(true)} apiState={apiState}/>{active === 'search' && <SearchPage/>}{active === 'minutes' && <MinutesPage/>}{active === 'report' && <ReportPage/>}</main></div>
}

createRoot(document.getElementById('root')).render(<App />)
