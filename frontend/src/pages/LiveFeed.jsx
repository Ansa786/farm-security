import { useEffect, useState } from 'react'
import Card from '../components/Card.jsx'
import CameraFeed from '../components/CameraFeed.jsx'
import { useSettings } from '../store/useStore'
import { getCameraStatus } from '../lib/api'

export default function LiveFeed() {
  const { streamUrl, apiBaseUrl } = useSettings()
  const [cameraStatus, setCameraStatus] = useState(null)

  useEffect(() => {
    const fetchStatus = async () => {
      const status = await getCameraStatus()
      setCameraStatus(status)
    }
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="grid gap-6">
      <Card title="Live Feed" subtitle="ESP32-CAM stream">
        <CameraFeed streamUrl={streamUrl} />
        {cameraStatus && (
          <div className="mt-4 p-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-white/60">Status:</span>{' '}
                <span className={cameraStatus.status === 'streaming' ? 'text-green-400' : 'text-red-400'}>
                  {cameraStatus.status || 'Unknown'}
                </span>
              </div>
              <div>
                <span className="text-white/60">System:</span>{' '}
                <span className={cameraStatus.system_active ? 'text-green-400' : 'text-yellow-400'}>
                  {cameraStatus.system_active ? 'Active' : 'Paused'}
                </span>
              </div>
              {cameraStatus.url && (
                <div className="col-span-2">
                  <span className="text-white/60">URL:</span>{' '}
                  <span className="text-white/80 font-mono text-xs">{cameraStatus.url}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </Card>
    </div>
  )
}
