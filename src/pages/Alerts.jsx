import { useEffect, useState } from 'react'
import Card from '../components/Card.jsx'
import AlertItem from '../components/AlertItem.jsx'
import { fetchAlerts } from '../lib/api.js'

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchAlerts()
        data.sort((a,b) => new Date(b.timestamp) - new Date(a.timestamp))
        setAlerts(data)
      } catch (e) {
        setError(e.message || 'Failed to load alerts')
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  return (
    <div className="grid gap-6">
      <Card title="Alerts" subtitle="Recent detections and events">
        {loading && <div className="text-white/80">Loading...</div>}
        {error && <div className="text-red-200">{error}</div>}
        {!loading && !error && (
          <div className="grid gap-3">
            {alerts.length === 0 && <div className="text-white/80">No alerts yet.</div>}
            {alerts.map((a,i) => <AlertItem key={i} alert={a} />)}
          </div>
        )}
      </Card>
    </div>
  )
}
