import { useEffect, useState } from 'react'
import Concierge from './pages/Concierge'
import Registry from './pages/Registry'
import { getModels } from './api'

export default function App() {
  const [room, setRoom] = useState('counter')
  const [mode, setMode] = useState('C')
  const [threshold, setThreshold] = useState(0.5)
  const [catalog, setCatalog] = useState({ default: '', models: [] })
  const [model, setModel] = useState('')
  useEffect(() => {
    getModels().then(c => { setCatalog(c); setModel(c.default) }).catch(() => {})
  }, [])
  const shared = { mode, setMode, threshold, setThreshold, model, setModel, catalog }
  return (
    <div className="grain min-h-screen">
      <header className="border-b border-brass/30">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-8 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full border-2 border-brass bg-green font-serif text-2xl text-brasslight">M</div>
            <div>
              <p className="font-serif text-[26px] leading-none tracking-wide text-green">MERIDIAN TRUST</p>
              <p className="smallcaps mt-1 text-ink/45">Private office · Est. MMXXVI</p>
            </div>
          </div>
          <div className="flex items-center gap-5">
            <label className="flex items-center gap-2">
              <span className="smallcaps text-ink/45">Mind</span>
              <select value={model} onChange={e => setModel(e.target.value)}
                className="cursor-pointer rounded-[2px] border border-brass/60 bg-[#FBF8EF] px-3 py-2 font-mono text-[11px] text-green outline-none">
                {catalog.models.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
              </select>
            </label>
            <nav className="flex items-center gap-7">
              {[['counter', 'The Counter'], ['registry', 'The Registry']].map(([k, l]) => (
                <button key={k} onClick={() => setRoom(k)}
                  className={`pb-1 font-serif text-[19px] italic transition ${room === k ? 'border-b-2 border-brass text-green' : 'text-ink/45 hover:text-green'}`}>{l}</button>
              ))}
            </nav>
          </div>
        </div>
      </header>
      <div className="rule-fan" />
      <main className="px-8 py-10">
        {room === 'counter' ? <Concierge {...shared} /> : <Registry {...shared} />}
      </main>
      <footer className="border-t border-brass/30 px-8 py-5 text-center">
        <p className="smallcaps text-ink/40">Sixteen houses of record · Fifty matters · Three charters</p>
      </footer>
    </div>
  )
}
