import { useEffect, useRef, useState } from 'react'
import { getLiveFeedUrl, getCameraStatus } from '../lib/api'

export default function CameraFeed({ streamUrl: propStreamUrl }) {
  const [error, setError] = useState(null)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const imgRef = useRef(null)

  useEffect(() => {
    // Fetch camera status
    getCameraStatus().then(data => {
      setStatus(data)
      setLoading(false)
    })

    // Use backend live feed URL if available, otherwise fallback to prop
    const feedUrl = getLiveFeedUrl() || propStreamUrl
    
    if (!feedUrl) {
      setError('No stream URL configured')
      setLoading(false)
      return
    }

    setError(null)
    if (imgRef.current) {
      imgRef.current.src = feedUrl
    }
  }, [propStreamUrl])

  if (loading) {
    return (
      <div className="aspect-video grid place-items-center rounded-xl border border-white/20 bg-panel backdrop-blur-md text-white/80">
        Connecting to camera...
      </div>
    )
  }

  if (!getLiveFeedUrl() && !propStreamUrl) {
    return (
      <div className="aspect-video grid place-items-center rounded-xl border border-white/20 bg-panel backdrop-blur-md text-white/80">
        No stream configured. Configure API Base URL in Settings.
      </div>
    )
  }

  const feedUrl = getLiveFeedUrl() || propStreamUrl
  const isBackendStream = feedUrl.includes('/camera/live_feed')

  return (
    <div className="relative">
      {status && (
        <div className="absolute top-2 right-2 z-10 px-3 py-1 rounded-lg bg-black/70 text-white text-xs">
          {status.status === 'streaming' ? '🟢 Streaming' : '🔴 Disconnected'}
          {status.system_active !== undefined && (
            <span className="ml-2">{status.system_active ? '⚡ Active' : '⏸️ Paused'}</span>
          )}
        </div>
      )}
      {isBackendStream ? (
        <img 
          ref={imgRef} 
          alt="Live stream" 
          className="aspect-video w-full rounded-xl border border-white/20 object-cover" 
          onError={() => setError('Failed to load stream')}
          onLoad={() => setError(null)}
        />
      ) : (
        <img 
          ref={imgRef} 
          alt="Live stream" 
          className="aspect-video w-full rounded-xl border border-white/20 object-cover" 
          onError={() => setError('Failed to load stream')}
          onLoad={() => setError(null)}
        />
      )}
      {error && (
        <div className="absolute inset-0 grid place-items-center bg-black/50 text-red-200 rounded-xl border border-white/20">
          {error}
        </div>
      )}
    </div>
  )
}
