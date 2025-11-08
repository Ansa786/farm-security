import { useEffect, useRef, useState } from 'react'

export default function CameraFeed({ streamUrl }) {
  const [error, setError] = useState(null)
  const imgRef = useRef(null)

  useEffect(() => {
    setError(null)
    if (!streamUrl) return
    if (imgRef.current) imgRef.current.src = streamUrl
  }, [streamUrl])

  if (!streamUrl) {
    return (
      <div className="aspect-video grid place-items-center rounded-xl border border-white/20 bg-panel backdrop-blur-md text-white/80">
        No stream configured. Add VITE_STREAM_URL in .env or use Settings.
      </div>
    )
  }

  return (
    <div className="relative">
      <img ref={imgRef} alt="Live stream" className="aspect-video w-full rounded-xl border border-white/20 object-cover" onError={() => setError('Failed to load stream')} />
      {error && <div className="absolute inset-0 grid place-items-center bg-black/50 text-red-200 rounded-xl border border-white/20">{error}</div>}
    </div>
  )
}
