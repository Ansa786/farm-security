import { useEffect, useState } from 'react'
import Card from '../components/Card.jsx'
import AlertItem from '../components/AlertItem.jsx'
import { fetchAlerts } from '../lib/api.js'

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadAlerts = async () => {
    try {
      const data = await fetchAlerts()
      // Sort by timestamp (newest first)
      const sorted = data.sort((a, b) => {
        const timeA = a.timestamp ? new Date(a.timestamp).getTime() : 0
        const timeB = b.timestamp ? new Date(b.timestamp).getTime() : 0
        return timeB - timeA
      })
      setAlerts(sorted)
      setError(null)
    } catch (e) {
      setError(e.message || 'Failed to load alerts')
      console.error('Error loading alerts:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAlerts()
    // Auto-refresh every 10 seconds
    const interval = setInterval(loadAlerts, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="grid gap-6">
      <Card title="Alerts" subtitle="Recent detections and events">
        <div className="flex justify-between items-center mb-4">
          <div className="text-sm text-white/60">
            {alerts.length} alert{alerts.length !== 1 ? 's' : ''} found
          </div>
          <div className="flex gap-2">
            <button 
              onClick={loadAlerts}
              disabled={loading}
              className="text-sm text-white/80 hover:text-white px-3 py-1 rounded-lg bg-white/10 hover:bg-white/20 border border-white/20 disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Refresh'}
            </button>
            <button 
              onClick={async () => {
                if (!confirm('Are you sure you want to clear all detection logs? This cannot be undone.')) {
                  return
                }
                try {
                  const { apiBaseUrl } = await import('../store/useStore').then(m => m.useSettings.getState())
                  const response = await fetch(`${apiBaseUrl}/api/events/clear`, { method: 'DELETE' })
                  if (response.ok) {
                    setAlerts([])
                    alert('✅ All logs cleared successfully!')
                  } else {
                    alert('❌ Failed to clear logs')
                  }
                } catch (error) {
                  console.error('Error clearing logs:', error)
                  alert('❌ Error: ' + error.message)
                }
              }}
              disabled={loading || alerts.length === 0}
              className="text-sm text-red-400 hover:text-red-300 px-3 py-1 rounded-lg bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Clear All
            </button>
          </div>
        </div>
        {loading && <div className="text-white/80">Loading alerts...</div>}
        {error && (
          <div className="text-red-200 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
            {error}
          </div>
        )}
        {!loading && !error && (
          <div className="grid gap-3">
            {alerts.length === 0 && (
              <div className="text-white/80 text-center py-8">
                No alerts yet. The system will show detection events here.
              </div>
            )}
            {alerts.map((a) => (
              <AlertItem key={a.id || a.timestamp} alert={a} />
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
