import Card from '../components/Card.jsx'
import { useSettings } from '../store/useStore'
import { setSystemEnabled } from '../lib/api'

export default function Settings() {
  const { apiBaseUrl, streamUrl, bgUrl, mock, _save } = useSettings()
  function setK(k, v) { _save({ [k]: v }) }
  async function test(type) { await setSystemEnabled(true); alert(type + ' test triggered') }

  return (
    <div className="grid gap-6">
      <Card title="Connection">
        <div className="grid gap-4 max-w-xl text-white">
          <label className="grid gap-1">
            <span className="text-sm text-white/80">API Base URL</span>
            <input className="rounded-lg border border-white/30 bg-black/20 px-3 py-2 text-white placeholder-white/60"
              value={apiBaseUrl} onChange={(e) => setK('apiBaseUrl', e.target.value)} placeholder="http://localhost:8000" />
          </label>
          <label className="grid gap-1">
            <span className="text-sm text-white/80">Stream URL (ESP32-CAM)</span>
            <input className="rounded-lg border border-white/30 bg-black/20 px-3 py-2 text-white placeholder-white/60"
              value={streamUrl} onChange={(e) => setK('streamUrl', e.target.value)} placeholder="http://<esp32-ip>:81/stream" />
          </label>
          <label className="grid gap-1">
            <span className="text-sm text-white/80">Background Image URL</span>
            <input className="rounded-lg border border-white/30 bg-black/20 px-3 py-2 text-white placeholder-white/60"
              value={bgUrl} onChange={(e) => setK('bgUrl', e.target.value)} placeholder="https://..." />
          </label>
          <label className="inline-flex items-center gap-2">
            <input type="checkbox" checked={mock} onChange={(e) => setK('mock', e.target.checked)} />
            <span className="text-sm">Use mock data</span>
          </label>
          <div className="flex gap-3 pt-2">
            <button onClick={() => test('siren')} className="rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 px-4 py-2 text-white">Test Siren</button>
            <button onClick={() => test('lights')} className="rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 px-4 py-2 text-white">Test Lights</button>
          </div>
        </div>
      </Card>
    </div>
  )
}
