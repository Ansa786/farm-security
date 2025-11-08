import classNames from 'classnames'
import { Power } from 'lucide-react'
import { useSystem } from '../store/useStore'
import { setSystemEnabled } from '../lib/api'

export default function SystemToggle({ className = '' }) {
  const { enabled } = useSystem()
  const onClick = () => setSystemEnabled(!enabled)

  return (
    <div className={classNames('rounded-2xl border border-white/15 bg-white/10 p-4 flex items-center justify-between backdrop-blur-md', className)}>
      <div className="flex items-center gap-2 text-white">
        <Power size={18} />
        <span className="text-sm">System</span>
      </div>
      <button onClick={onClick} className={classNames('relative inline-flex h-7 w-12 items-center rounded-full transition', enabled ? 'bg-green-500' : 'bg-red-500')} aria-label="Toggle system">
        <span className={classNames('inline-block h-5 w-5 transform rounded-full bg-white transition', enabled ? 'translate-x-6' : 'translate-x-1')} />
      </button>
    </div>
  )
}
