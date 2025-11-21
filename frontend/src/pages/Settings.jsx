import { useEffect, useState } from 'react'
import Card from '../components/Card.jsx'
import { useSettings } from '../store/useStore'
import { toggleSiren, getSystemStatus, getCameraStatus } from '../lib/api'

export default function Settings() {
  const { apiBaseUrl, streamUrl, bgUrl, mock, _save } = useSettings()
  const [systemStatus, setSystemStatus] = useState(null)
  const [cameraStatus, setCameraStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  function setK(k, v) { _save({ [k]: v }) }

  useEffect(() => {
    if (!mock && apiBaseUrl) {
      const fetchStatus = async () => {
        try {
          const [sysStatus, camStatus] = await Promise.all([
            getSystemStatus(),
            getCameraStatus()
          ])
          setSystemStatus(sysStatus)
          setCameraStatus(camStatus)
        } catch (error) {
          console.error('Failed to fetch status:', error)
        }
      }
      fetchStatus()
      const interval = setInterval(fetchStatus, 5000)
      return () => clearInterval(interval)
    }
  }, [mock, apiBaseUrl])

  async function testSiren() {
    setLoading(true)
    try {
      const result = await toggleSiren('ON')
      alert(result.success ? 'Siren activated!' : 'Failed to activate siren')
      setTimeout(async () => {
        await toggleSiren('OFF')
      }, 2000)
    } catch (error) {
      alert('Failed to test siren: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid gap-6">
      <Card title="Connection">
        <div className="grid gap-4 max-w-xl text-white">
          <label className="grid gap-1">
            <span className="text-sm text-white/80">API Base URL</span>
            <input className="rounded-lg border border-white/30 bg-black/20 px-3 py-2 text-white placeholder-white/60"
              value={apiBaseUrl} onChange={(e) => setK('apiBaseUrl', e.target.value)} placeholder="http://localhost:8000" />
            <span className="text-xs text-white/50">Backend API endpoint (e.g., http://localhost:8000)</span>
          </label>
          <label className="grid gap-1">
            <span className="text-sm text-white/80">Stream URL (Fallback)</span>
            <input className="rounded-lg border border-white/30 bg-black/20 px-3 py-2 text-white placeholder-white/60"
              value={streamUrl} onChange={(e) => setK('streamUrl', e.target.value)} placeholder="http://192.168.43.77/" />
            <span className="text-xs text-white/50">Direct camera URL (used if API Base URL not set)</span>
          </label>
          <label className="grid gap-1">
            <span className="text-sm text-white/80">Background Image URL</span>
            <input className="rounded-lg border border-white/30 bg-black/20 px-3 py-2 text-white placeholder-white/60"
              value={bgUrl} onChange={(e) => setK('bgUrl', e.target.value)} placeholder="https://..." />
          </label>
          <label className="inline-flex items-center gap-2">
            <input type="checkbox" checked={mock} onChange={(e) => setK('mock', e.target.checked)} />
            <span className="text-sm">Use mock data (disables API calls)</span>
          </label>
        </div>
      </Card>

      {!mock && apiBaseUrl && (
        <>
          <Card title="System Status">
            <div className="grid gap-3 text-white">
              {systemStatus ? (
                <>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-white/80">System Status:</span>
                    <span className={`font-medium ${systemStatus.status === 'ON' ? 'text-green-400' : 'text-red-400'}`}>
                      {systemStatus.status_display || systemStatus.status}
                      {systemStatus.camera_connected && systemStatus.status === 'ON' && (
                        <span className="ml-2 text-green-300">• Connected</span>
                      )}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-white/80">Siren State:</span>
                    <span className={`font-medium ${systemStatus.siren_state === 'ON' ? 'text-yellow-400' : 'text-gray-400'}`}>
                      {systemStatus.siren_state}
                    </span>
                  </div>
                  <div className="text-xs text-white/60 mt-2">{systemStatus.message}</div>
                </>
              ) : (
                <div className="text-sm text-white/60">Loading status...</div>
              )}
            </div>
          </Card>

          <Card title="Camera Status">
            <div className="grid gap-3 text-white">
              {cameraStatus ? (
                <>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-white/80">Stream Status:</span>
                    <span className={`font-medium ${cameraStatus.status === 'streaming' ? 'text-green-400' : 'text-red-400'}`}>
                      {cameraStatus.status}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-white/80">System Active:</span>
                    <span className={`font-medium ${cameraStatus.system_active ? 'text-green-400' : 'text-yellow-400'}`}>
                      {cameraStatus.system_active ? 'Yes' : 'No'}
                    </span>
                  </div>
                  {cameraStatus.url && (
                    <div className="text-xs text-white/60 mt-2 font-mono break-all">
                      URL: {cameraStatus.url}
                    </div>
                  )}
                </>
              ) : (
                <div className="text-sm text-white/60">Loading status...</div>
              )}
            </div>
          </Card>
        </>
      )}

      <Card title="Push Notifications">
        <div className="grid gap-3 text-white">
          <p className="text-sm text-white/80">
            Enable push notifications to receive alerts when intrusions are detected.
          </p>
          <button 
            onClick={async () => {
              console.log('Enable Notifications clicked')
              try {
                if (!window.OneSignal) {
                  alert('❌ OneSignal not loaded. Please refresh the page.')
                  return
                }
                
                console.log('Requesting permission...')
                const permission = await window.OneSignal.Notifications.requestPermission()
                console.log('Permission result:', permission)
                
                if (permission) {
                  console.log('Getting player ID...')
                  const playerId = await window.OneSignal.User.PushSubscription.id
                  console.log('Player ID:', playerId)
                  
                  if (playerId) {
                    alert(`✅ Subscribed! Your Player ID: ${playerId}\n\nYou will now receive intrusion alerts.`)
                  } else {
                    alert('⚠️ Permission granted but no Player ID yet. Try again in a moment.')
                  }
                } else {
                  alert('❌ Notification permission denied. Please enable notifications in your browser settings.')
                }
              } catch (error) {
                console.error('Notification error:', error)
                alert('Error: ' + error.message)
              }
            }}
            className="rounded-xl bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/40 px-4 py-2 text-white w-fit"
          >
            📱 Enable Notifications
          </button>
          <button 
            onClick={async () => {
              console.log('Check Status clicked')
              try {
                if (!window.OneSignal) {
                  alert('❌ OneSignal not loaded. Please refresh the page.')
                  return
                }
                
                const playerId = await window.OneSignal.User.PushSubscription.id
                console.log('Current Player ID:', playerId)
                
                if (playerId) {
                  alert(`✅ You are subscribed!\n\nPlayer ID: ${playerId}`)
                } else {
                  alert('❌ Not subscribed. Click "Enable Notifications" above.')
                }
              } catch (error) {
                console.error('Status check error:', error)
                alert('Error: ' + error.message)
              }
            }}
            className="rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 px-4 py-2 text-white w-fit text-sm"
          >
            Check Subscription Status
          </button>
        </div>
      </Card>

      <Card title="Test Controls">
        <div className="flex gap-3">
          <button 
            onClick={testSiren} 
            disabled={loading || mock}
            className="rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 px-4 py-2 text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Testing...' : 'Test Siren'}
          </button>
        </div>
        {mock && (
          <div className="text-xs text-yellow-400 mt-2">
            Enable API connection to use test controls
          </div>
        )}
      </Card>
    </div>
  )
}
