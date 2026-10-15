import { useEffect, useRef, useState } from 'react'
import { postChat, shortModel } from '../api'

const EXEMPLARS = [
  'What are the eligibility criteria for an HDFC personal loan?',
  'How do I report an MUFG impersonation scam?',
  'Should I invest my savings in crypto?',
  'Is this $4999 charge definitely fraud?',
]

const CHARTERS = [
  ['A', 'I · Forthcoming', 'Answers wherever the record allows'],
  ['B', 'II · Circumspect', 'Declines beneath a confidence mark'],
  ['C', 'III · Resolute', 'Declines outright whenever unsure'],
]

const STAGES = [
  ['presented', 'Presented at the counter'],
  ['retrieving', 'Searching the sixteen houses'],
  ['drafting', 'Drafting from the record'],
  ['reviewing', 'Compliance review'],
  ['sealed', 'Reply sealed'],
]

function Procession({ events }) {
  const order = Object.fromEntries(STAGES.map(([s], i) => [s, i]))
  const reached = events.reduce((m, e) => Math.max(m, order[e.stage] ?? 0), 0)
  const cur = events[events.length - 1]
  return (
    <div className="enter rounded-sm border border-brass/50 bg-green px-6 py-5 text-paper">
      <p className="smallcaps mb-4 text-brasslight">❦ The matter is in hand</p>
      <ol className="space-y-2.5">
        {STAGES.map(([s, label], i) => (
          <li key={s} className="flex items-center gap-3 text-[13px]">
            <span className={`flex h-6 w-6 items-center justify-center rounded-full border font-serif text-[13px] ${i < reached ? 'border-brasslight bg-brass text-green' : i === reached ? 'border-brasslight text-brasslight' : 'border-paper/25 text-paper/35'}`}>
              {i < reached ? '✓' : i === reached ? <span className="quill">❦</span> : (i + 1)}
            </span>
            <span className={i <= reached ? 'font-serif text-[16px] italic' : 'text-paper/35'}>{label}</span>
            {i === reached && cur?.elapsed != null && <span className="font-mono text-[10px] text-paper/45">{cur.elapsed}s</span>}
          </li>
        ))}
      </ol>
      {cur?.detail && <p className="mt-3 border-t border-paper/15 pt-2 font-serif text-[14px] italic text-paper/70">{cur.detail}</p>}
    </div>
  )
}

function Assurance({ v }) {
  return (
    <span className="inline-flex items-center gap-2">
      <span className="inline-block h-[3px] w-20 overflow-hidden rounded bg-ink/10">
        <span className="block h-full bg-brass" style={{ width: `${Math.round(v * 100)}%` }} />
      </span>
      <span className="font-mono text-[10px] text-ink/50">assurance {v.toFixed(2)}</span>
    </span>
  )
}

export default function Concierge({ mode, setMode, threshold, setThreshold, model }) {
  const [ledger, setLedger] = useState([
    { role: 'house', text: 'Good day. This is the private counter of Meridian Trust. Enquire of loans, papers, or the reporting of fraud — and where the record is silent, the house will say so plainly.' },
  ])
  const [draft, setDraft] = useState('')
  const [writing, setWriting] = useState(false)
  const [trail, setTrail] = useState([])
  const scroll = useRef(null)
  useEffect(() => { scroll.current?.scrollTo({ top: 1e9, behavior: 'smooth' }) }, [ledger, writing])

  async function present(text) {
    const q = (text ?? draft).trim()
    if (!q || writing) return
    setDraft('')
    setLedger(l => [...l, { role: 'guest', text: q }])
    setWriting(true)
    setTrail([])
    try {
      const r = await postChat(q, mode, threshold, model, setTrail)
      setLedger(l => [...l, { role: 'house', ...r, text: r.answer }])
    } catch (e) {
      setLedger(l => [...l, { role: 'house', text: String((e && e.message) || e), error: true }])
    }
    setWriting(false)
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-190px)] max-w-2xl flex-col">
      <div className="enter mb-8 text-center">
        <p className="smallcaps text-brass">The Counter · Sixteen Houses of Record</p>
        <h1 className="font-serif mt-3 text-6xl leading-[1.02] text-green">State your<br /><em className="font-normal">business.</em></h1>
        <div className="rule-foil mx-auto mt-6 w-56" />
      </div>

      <div className="mb-5 grid grid-cols-3 gap-2">
        {CHARTERS.map(([m, name, sub]) => (
          <button key={m} onClick={() => setMode(m)}
            className={`rounded-sm border px-3 py-3 text-left transition ${mode === m ? 'border-brass bg-green text-paper shadow-[0_10px_30px_-12px_#0c2b23]' : 'border-ink/15 bg-white/40 hover:border-brass/60'}`}>
            <p className={`font-mono text-[10px] tracking-[0.2em] ${mode === m ? 'text-brasslight' : 'text-brass'}`}>{name}</p>
            <p className={`mt-1 text-[11px] leading-snug ${mode === m ? 'text-paper/70' : 'text-ink/55'}`}>{sub}</p>
          </button>
        ))}
      </div>
      {mode === 'B' && (
        <label className="mx-auto mb-5 flex items-center gap-3 text-xs text-ink/60">
          <span className="smallcaps">The mark</span>
          <input type="range" min="0.1" max="0.9" step="0.1" value={threshold} onChange={e => setThreshold(+e.target.value)} className="w-40" />
          <span className="font-mono text-brass">{threshold.toFixed(1)}</span>
        </label>
      )}

      <div ref={scroll} className="scroll-thin frame flex-1 space-y-7 overflow-y-auto rounded-sm bg-[#FBF8EF] p-8">
        {ledger.map((m, i) => m.role === 'guest' ? (
          <div key={i} className="enter ml-auto max-w-[80%]">
            <p className="smallcaps mb-1 text-right text-ink/40">Yourself</p>
            <p className="rounded-sm border border-brass/60 bg-parchment px-5 py-3.5 text-[15px] leading-relaxed">{m.text}</p>
          </div>
        ) : (
          <div key={i} className="enter flex max-w-[92%] gap-4">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full border border-brass bg-green font-serif text-xl text-brasslight">M</div>
            <div className="min-w-0">
              <p className="smallcaps mb-1 text-ink/40">The House</p>
              <div className={`rounded-sm border px-5 py-4 text-[15px] leading-relaxed ${m.error ? 'border-[#8c2f2f]/40 bg-[#8c2f2f]/5' : m.abstained ? 'border-brass bg-brass/[0.07]' : 'border-ink/10 bg-white/60'}`}>
                {m.abstained && <p className="smallcaps mb-2 border-b border-brass/30 pb-2 text-brass">❦ Declined — referred to a specialist</p>}
                <p className="whitespace-pre-wrap font-serif text-[17px]">{m.text}</p>
                {m.confidence != null && (
                  <p className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-ink/10 pt-2 font-sans text-xs">
                    <Assurance v={m.confidence} />
                    {m.latency != null && <span className="font-mono text-[10px] text-ink/45">{m.latency}s at the desk · {shortModel(m.model)}</span>}
                  </p>
                )}
                {m.sources?.length > 0 && <p className="mt-1 font-mono text-[10px] text-ink/45">folio: {m.sources.map(s => s.file?.replace('.md', '')).join(' · ')}</p>}
              </div>
            </div>
          </div>
        ))}
        {writing && (
          <Procession events={trail} />
        )}
      </div>

      <div className="mt-4 flex flex-wrap justify-center gap-2">
        {EXEMPLARS.map(s => <button key={s} onClick={() => present(s)} className="border-b border-brass/50 pb-0.5 font-serif text-[14px] italic text-ink/60 transition hover:text-green">{s}</button>)}
      </div>
      <div className="frame mt-4 flex items-center gap-2 rounded-sm bg-green p-2 pl-6">
        <input value={draft} onChange={e => setDraft(e.target.value)} onKeyDown={e => e.key === 'Enter' && present()}
          placeholder="Write your enquiry…" className="flex-1 bg-transparent text-[15px] text-paper outline-none placeholder:text-paper/35" />
        <button onClick={() => present()} disabled={writing} className="rounded-[2px] bg-brass px-7 py-2.5 font-mono text-[11px] font-medium uppercase tracking-[0.2em] text-green transition hover:bg-brasslight disabled:opacity-40">Present</button>
      </div>
    </div>
  )
}
