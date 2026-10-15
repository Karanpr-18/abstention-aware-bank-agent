import { useEffect, useMemo, useState } from 'react'
import { getQuestions, runEval, quickVerdict, TYPE_META, GOLD_LABEL, shortModel } from '../api'

const SEAL = {
  correct: 'border-green/50 text-green',
  appropriate_abstain: 'border-[#2f5f8c]/50 text-[#2f5f8c]',
  inappropriate_abstain: 'border-brass/60 text-[#7a5f22]',
  false_confidence: 'border-[#8c2f2f]/60 text-[#8c2f2f]',
}
const SEAL_WORD = { correct: 'Sound', appropriate_abstain: 'Properly declined', inappropriate_abstain: 'Over-cautious', false_confidence: 'False confidence' }

async function getBatches() {
  const r = await fetch('/api/batches')
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
async function startBatch(batch, mode, threshold, model) {
  const r = await fetch('/api/eval/batch', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ batch, mode, threshold, model }),
  })
  if (!r.ok) {
    let msg = await r.text()
    try { msg = JSON.parse(msg).detail || msg } catch { /* plain */ }
    throw new Error(msg)
  }
  return r.json()
}
async function pollBatch(jobId, onTick) {
  for (let i = 0; i < 1500; i++) {
    const r = await fetch(`/api/jobs/${jobId}`)
    if (!r.ok) {
      let msg = await r.text()
      try { msg = JSON.parse(msg).detail || msg } catch { /* plain */ }
      throw new Error(`Lost the batch trail (${r.status}): ${msg}. Restart the server run and convene again — heard matters are kept.`)
    }
    const j = await r.json()
    if (onTick) onTick(j)
    if (j.status === 'done') return j.result
    if (j.status === 'error') throw new Error((j.error && j.error.message) || 'Batch failed.')
    await new Promise(res => setTimeout(res, 2000))
  }
  throw new Error('The batch wait grew too long — convene again to resume the unheard matters.')
}

export default function Registry({ mode, setMode, threshold, setThreshold, model }) {
  const [batches, setBatches] = useState([])
  const [batch, setBatch] = useState(1)
  const [matters, setMatters] = useState([])
  const [rulings, setRulings] = useState({})
  const [calling, setCalling] = useState(null)
  const [running, setRunning] = useState(false)
  const [judging, setJudging] = useState(false)
  const [judged, setJudged] = useState(null)
  const [hearing, setHearing] = useState('')
  const [live, setLive] = useState({})
  const [ready, setReady] = useState(false)
  const [err, setErr] = useState('')

  useEffect(() => { getBatches().then(setBatches).catch(e => setErr(String(e))) }, [])
  useEffect(() => {
    fetch(`/api/questions?batch=${batch}`).then(r => r.json()).then(setMatters).catch(e => setErr(String(e)))
    setReady(false); setJudged(null)
  }, [batch])

  const done = Object.values(rulings).filter(r => !r.error && r.batchDone !== false)
  const batchRows = useMemo(() => matters.map(q => rulings[q.id]).filter(Boolean), [matters, rulings])
  const tally = useMemo(() => ({
    n: batchRows.filter(r => !r.error).length,
    sound: batchRows.filter(r => !r.error && ['correct', 'appropriate_abstain'].includes(quickVerdict(r.gold, r.answer, r.abstained))).length,
    unsound: batchRows.filter(r => !r.error && quickVerdict(r.gold, r.answer, r.abstained) === 'false_confidence').length,
    failed: batchRows.filter(r => r.error).length,
  }), [batchRows])

  async function callOne(q) {
    setCalling({ qid: q.id, trail: [] })
    try {
      const r = await runEval(q.id, mode, threshold, model, ev => setCalling(c => (c && c.qid === q.id ? { ...c, trail: ev } : c)))
      setRulings(p => ({ ...p, [q.id]: r }))
    } catch (e) { setErr(String((e && e.message) || e)) }
    setCalling(null)
  }
  async function convene() {
    setRunning(true); setErr(''); setReady(false)
    try {
      const { job_id } = await startBatch(batch, mode, threshold, model)
      const res = await pollBatch(job_id, j => {
        const last = (j.events || []).slice(-1)[0]
        setHearing(`${j.done || 0} / 20${last ? ' · ' + last.detail : ''}`)
        const per = {}
        for (const ev of (j.events || [])) {
          const d = ev.detail || ''
          let m = d.match(/^\[([^\]]+)\]\s*(.*)$/)
          if (m) { per[m[1]] = { stage: ev.stage, detail: m[2], elapsed: ev.elapsed }; continue }
          m = d.match(/Matter \d+\/\d+ · (\S+)/)
          if (m) per[m[1]] = { stage: ev.stage, detail: d, elapsed: ev.elapsed }
        }
        setLive(per)
        if (j.done_rows && j.done_rows.length) {
          const merged = {}
          for (const r of j.done_rows) merged[r.qid] = r
          setRulings(p => ({ ...p, ...merged }))
        }
      })
      const merged = {}
      for (const r of res.rows) merged[r.qid] = r
      setRulings(p => ({ ...p, ...merged }))
      setReady(true)
    } catch (e) { setErr(String((e && e.message) || e)) }
    setCalling(null); setHearing(''); setLive({}); setRunning(false)
  }

  const xlsx = `/api/eval/batch/${batch}/xlsx?mode=${encodeURIComponent(mode)}&model=${encodeURIComponent(model)}`

  async function judgeBatch() {
    setJudging(true); setErr('')
    try {
      const s = await fetch('/api/eval/batch/judge', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ batch, mode, model }),
      })
      if (!s.ok) throw new Error(await s.text())
      const { job_id } = await s.json()
      for (let i = 0; i < 900; i++) {
        const j = await (await fetch(`/api/jobs/${job_id}`)).json()
        const last = (j.events || []).slice(-1)[0]
        setHearing(`judging ${j.done_rows ? j.done_rows.length : 0} / 20${last ? ' · ' + last.detail : ''}`)
        if (j.status === 'done') { setJudged(j.result); break }
        if (j.status === 'error') throw new Error((j.error && j.error.message) || 'Judge failed.')
        await new Promise(res => setTimeout(res, 2000))
      }
    } catch (e) { setErr(String((e && e.message) || e)) }
    setHearing(''); setJudging(false)
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="enter mb-8 text-center">
        <p className="smallcaps text-brass">For the researcher\u2019s eyes only · the clerk\u2019s margin never reaches the house</p>
        <h1 className="font-serif mt-3 text-6xl text-green">Registry <em className="font-normal">of One Hundred.</em></h1>
        <div className="rule-foil mx-auto mt-6 w-56" />
      </div>

      <div className="mb-6 flex flex-wrap justify-center gap-2">
        {batches.map(b => (
          <button key={b.n} onClick={() => setBatch(b.n)}
            className={`rounded-[2px] border px-5 py-2.5 font-mono text-[11px] uppercase tracking-[0.18em] ${batch === b.n ? 'border-green bg-green text-paper' : 'border-ink/15 text-ink/50 hover:border-brass'}`}>
            Batch {b.n} · {b.size}
          </button>
        ))}
      </div>

      <div className="frame mb-6 flex flex-wrap items-center justify-between gap-4 rounded-sm bg-green px-6 py-4 text-paper">
        <div className="flex items-center gap-4">
          <div className="flex gap-1.5">
            {['A', 'B', 'C'].map(m => (
              <button key={m} onClick={() => setMode(m)} className={`h-9 w-9 rounded-full border font-serif text-lg transition ${mode === m ? 'border-brasslight bg-brass text-green' : 'border-paper/30 text-paper/60 hover:border-brasslight'}`}>{m}</button>
            ))}
          </div>
          <p className="text-xs text-paper/60">Charter {mode}{mode === 'B' ? ` · mark ${threshold.toFixed(1)}` : ''}</p>
          {mode === 'B' && <input type="range" min="0.1" max="0.9" step="0.1" value={threshold} onChange={e => setThreshold(+e.target.value)} className="w-28" />}
        </div>
        <div className="flex items-center gap-2">
          <button onClick={convene} disabled={running || !matters.length} className="rounded-[2px] bg-brass px-6 py-2.5 font-mono text-[11px] uppercase tracking-[0.2em] text-green hover:bg-brasslight disabled:opacity-40">
            {running ? `Hearing ${hearing || '…'}` : `Convene batch ${batch}`}
          </button>
          {ready && !running && (
            <button onClick={judgeBatch} disabled={judging}
              className="rounded-[2px] border border-brasslight px-6 py-2.5 font-mono text-[11px] uppercase tracking-[0.2em] text-brasslight hover:bg-brass hover:text-green disabled:opacity-40">
              {judging ? `Judging ${hearing || '…'}` : 'Judge batch'}
            </button>
          )}
          {ready && !running && (
            <a href={xlsx} className="rounded-[2px] border border-brasslight px-6 py-2.5 font-mono text-[11px] uppercase tracking-[0.2em] text-brasslight hover:bg-brass hover:text-green">
              Download Excel{judged ? ` · ${judged.satisfied}/${judged.total} satisfied` : ''}
            </a>
          )}
        </div>
      </div>
      {running && <div className="rule-foil mb-6" />}
      {tally.n > 0 && (
        <p className="mb-6 text-center font-serif text-xl italic text-ink/70">
          {tally.n} matters heard — <span className="text-green">{tally.sound} sound</span>, <span className="text-[#8c2f2f]">{tally.unsound} falsely confident</span>{tally.failed > 0 && <span> · {tally.failed} unheard</span>}.
        </p>
      )}
      {err && <p className="mb-4 border border-[#8c2f2f]/40 bg-[#8c2f2f]/5 px-4 py-2 text-xs">{err}</p>}

      <ol className="scroll-thin max-h-[calc(100vh-470px)] space-y-5 overflow-y-auto pb-10">
        {matters.map((q, n) => {
          const r = rulings[q.id]
          const v = r && !r.error ? quickVerdict(r.gold, r.answer, r.abstained) : null
          return (
            <li key={q.id} className="enter frame rounded-[2px] bg-[#FBF8EF] p-7">
              <div className="flex items-start justify-between gap-5">
                <div className="flex min-w-0 gap-5">
                  <span className="font-serif text-4xl leading-none text-brass/70">{String(n + 1).padStart(2, '0')}</span>
                  <div className="min-w-0">
                    <p className="mb-2 flex flex-wrap items-center gap-2">
                      <span className={`rounded-full border px-2.5 py-0.5 font-mono text-[9px] uppercase tracking-[0.18em] ${TYPE_META[q.type].stamp}`}>{TYPE_META[q.type].label}</span>
                      <span className="font-mono text-[10px] text-ink/40">clerk expects · <b className="text-brass">{GOLD_LABEL[q.gold]}</b></span>
                    </p>
                    <p className="font-serif text-[21px] leading-snug">{q.query}</p>
                    {q.note && <p className="mt-1.5 text-xs italic text-ink/50">{q.note}</p>}
                  </div>
                </div>
                <button onClick={() => callOne(q)} disabled={(calling && calling.qid === q.id) || running}
                  className="shrink-0 rounded-[2px] border border-green px-5 py-2 font-mono text-[10px] uppercase tracking-[0.2em] text-green transition hover:bg-green hover:text-paper disabled:opacity-40">
                  {calling && calling.qid === q.id ? 'Calling…' : r && !r.error ? 'Recall' : 'Call'}
                </button>
              </div>
              {calling && calling.qid === q.id && (
                <p className="ml-[60px] mt-3 font-serif text-[14px] italic text-brass">
                  <span className="quill">❦</span> {(() => { const ev = calling.trail[calling.trail.length - 1]; return ev ? `${ev.stage} — ${ev.detail || ''} (${ev.elapsed}s)` : 'presenting…' })()}
                </p>
              )}
              {running && !r && live[q.id] && (
                <p className="ml-[60px] mt-3 font-serif text-[14px] italic text-brass">
                  <span className="quill">❦</span> {live[q.id].stage} — {live[q.id].detail} ({live[q.id].elapsed}s)
                </p>
              )}
              {running && !r && !live[q.id] && (
                <p className="ml-[60px] mt-3 font-serif text-[14px] italic text-ink/40">Awaiting its turn…</p>
              )}
              {r && r.error && (
                <p className="ml-[60px] mt-3 border-l-2 border-[#8c2f2f]/50 pl-5 font-serif text-[14px] italic text-[#8c2f2f]">Unheard — {r.error}</p>
              )}
              {r && !r.error && (
                <div className="ml-[60px] mt-4 border-l-2 border-brass/50 pl-5">
                  <p className="mb-1.5 flex flex-wrap items-center gap-3">
                    <span className={`rounded-full border px-2.5 py-0.5 font-mono text-[9px] uppercase tracking-[0.18em] ${SEAL[v]}`}>❦ {SEAL_WORD[v]}</span>
                    <span className="font-mono text-[10px] text-ink/45">assurance {r.confidence.toFixed(2)} · {r.latency}s · charter {r.mode} · {shortModel(r.model)}</span>
                  </p>
                  <p className="whitespace-pre-wrap font-serif text-[16.5px] leading-relaxed text-ink/85">{r.answer}</p>
                </div>
              )}
            </li>
          )
        })}
      </ol>
    </div>
  )
}
