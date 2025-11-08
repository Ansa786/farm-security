export default function AlertItem({ alert }) {
  const dt = new Date(alert.timestamp)
  const formatted = dt.toLocaleString(undefined, { day: '2-digit', month: '2-digit', year: 'numeric', hour: 'numeric', minute: '2-digit', second: '2-digit' })
  const kind = (alert.type || '').toLowerCase() === 'human' ? 'Human' : 'Animal/Other'

  return (
    <div className="rounded-xl border border-white/20 p-4 bg-panel backdrop-blur-md text-white">
      <div className="flex items-center justify-between">
        <div>
          <div className="font-medium">{formatted}{alert.location ? `, ${alert.location}` : ''}</div>
          <div className="text-sm text-white/80 mt-1">{kind} Detected ({(alert.type || '').toUpperCase()})</div>
        </div>
      </div>
    </div>
  )
}
