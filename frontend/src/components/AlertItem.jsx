export default function AlertItem({ alert }) {
  let formatted = 'Unknown time'
  if (alert.timestamp) {
    try {
      const dt = new Date(alert.timestamp)
      if (!isNaN(dt.getTime())) {
        formatted = dt.toLocaleString(undefined, { 
          day: '2-digit', 
          month: '2-digit', 
          year: 'numeric', 
          hour: 'numeric', 
          minute: '2-digit', 
          second: '2-digit' 
        })
      }
    } catch (e) {
      console.error('Error parsing timestamp:', e)
    }
  }
  
  const detectionType = alert.type || alert.detection_type || 'Unknown'
  const kind = detectionType.toLowerCase().includes('human') || detectionType.toLowerCase().includes('person') 
    ? 'Human' 
    : detectionType.toLowerCase().includes('elephant') 
    ? 'Elephant' 
    : detectionType.toLowerCase().includes('cow')
    ? 'Cow'
    : 'Animal/Other'
  const device = alert.device || alert.device_id || 'Unknown Device'
  const confidence = alert.confidence ? (alert.confidence * 100).toFixed(1) : null

  return (
    <div className="rounded-xl border border-white/20 p-4 bg-panel backdrop-blur-md text-white">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="font-medium text-white">{formatted}</div>
          <div className="text-sm text-white/80 mt-1">
            <span className="font-semibold">{kind}</span> Detected ({detectionType.toUpperCase()})
            {confidence && <span className="ml-2 text-white/60">• {confidence}% confidence</span>}
          </div>
          <div className="text-xs text-white/60 mt-2">
            Device: {device}
          </div>
          <div className="flex gap-3 mt-2 flex-wrap">
            {alert.siren !== undefined && (
              <span className={`text-xs px-2 py-1 rounded ${alert.siren ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-500/20 text-gray-400'}`}>
                {alert.siren ? '🔊 Siren' : '🔇 No Siren'}
              </span>
            )}
            {alert.notified !== undefined && (
              <span className={`text-xs px-2 py-1 rounded ${alert.notified ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
                {alert.notified ? '📱 Notified' : '📵 No Notification'}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
