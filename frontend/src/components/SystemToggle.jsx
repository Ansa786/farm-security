import { useEffect, useState } from 'react'
import classNames from 'classnames'
import { Power } from 'lucide-react'
import { useSystem } from '../store/useStore'
import { setSystemEnabled, getSystemStatus } from '../lib/api'

export default function SystemToggle({ className = '' }) {
  const { enabled, _save } = useSystem()
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState(null)

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await getSystemStatus()
        setStatus(data)
        // Sync with store
        const isEnabled = data.status === 'ON'
        if (isEnabled !== enabled) {
          _save({ enabled: isEnabled })
        }
      } catch (error) {
        console.error('Failed to fetch system status:', error)
      }
    }
    fetchStatus()
    const interval = setInterval(fetchStatus, 3000) // Refresh every 3 seconds
    return () => clearInterval(interval)
  }, [enabled, _save])

  const onClick = async () => {
    setLoading(true)
    try {
      await setSystemEnabled(!enabled)
      // Status will update via interval
    } catch (error) {
      console.error('Failed to toggle system:', error)
    } finally {
      setLoading(false)
    }
  }

  const isEnabled = status?.status === 'ON' || enabled
  const sirenState = status?.siren_state

  return (
    <div className={classNames('rounded-2xl border border-white/15 bg-white/10 p-4 flex items-center justify-between backdrop-blur-md', className)}>
      <div className="flex items-center gap-2 text-white">
        <Power size={18} />
        <div className="flex flex-col">
          <span className="text-sm font-medium">System</span>
          {status && (
            <span className="text-xs text-white/60">
              {status.message || (isEnabled ? 'Active' : 'Paused')}
              {sirenState && ` • Siren: ${sirenState}`}
            </span>
          )}
        </div>
      </div>
      <button 
        onClick={onClick} 
        disabled={loading}
        className={classNames(
          'relative inline-flex h-7 w-12 items-center rounded-full transition',
          isEnabled ? 'bg-green-500' : 'bg-red-500',
          loading && 'opacity-50 cursor-not-allowed'
        )} 
        aria-label="Toggle system"
      >
        <span className={classNames('inline-block h-5 w-5 transform rounded-full bg-white transition', isEnabled ? 'translate-x-6' : 'translate-x-1')} />
      </button>
    </div>
  )
}
