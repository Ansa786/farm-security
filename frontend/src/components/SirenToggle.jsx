import { useState } from 'react'
import classNames from 'classnames'
import { Volume2, VolumeX } from 'lucide-react'
import { toggleSiren } from '../lib/api'

export default function SirenToggle({ className = '' }) {
  const [loading, setLoading] = useState(false)
  const [sirenOn, setSirenOn] = useState(false)

  const onClick = async () => {
    setLoading(true)
    try {
      const action = sirenOn ? 'OFF' : 'ON'
      const result = await toggleSiren(action)
      if (result.success) {
        setSirenOn(!sirenOn)
      } else {
        alert('Failed to toggle siren: ' + (result.message || 'Unknown error'))
      }
    } catch (error) {
      console.error('Failed to toggle siren:', error)
      alert('Error toggling siren: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={classNames('rounded-2xl border border-white/15 bg-white/10 p-4 flex items-center justify-between backdrop-blur-md', className)}>
      <div className="flex items-center gap-2 text-white">
        {sirenOn ? <Volume2 size={18} /> : <VolumeX size={18} />}
        <div className="flex flex-col">
          <span className="text-sm font-medium">Siren Control</span>
          <span className="text-xs text-white/60">
            {sirenOn ? 'Siren is ON' : 'Siren is OFF'}
          </span>
        </div>
      </div>
      <button 
        onClick={onClick} 
        disabled={loading}
        className={classNames(
          'relative inline-flex h-7 w-12 items-center rounded-full transition',
          sirenOn ? 'bg-yellow-500' : 'bg-gray-500',
          loading && 'opacity-50 cursor-not-allowed'
        )} 
        aria-label="Toggle siren"
      >
        <span className={classNames('inline-block h-5 w-5 transform rounded-full bg-white transition', sirenOn ? 'translate-x-6' : 'translate-x-1')} />
      </button>
    </div>
  )
}
