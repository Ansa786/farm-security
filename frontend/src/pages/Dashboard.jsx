import { Link } from 'react-router-dom'
import Card from '../components/Card.jsx'
import SystemToggle from '../components/SystemToggle.jsx'
import SirenToggle from '../components/SirenToggle.jsx'
import { Play, Bell, Settings } from 'lucide-react'

export default function Dashboard() {
  return (
    <div className="grid gap-6 place-items-start">
      <div className="w-full md:w-[640px] lg:w-[720px]">
        <Card title="Quick Actions">
          <div className="grid gap-4">
            <Link to="/live" className="flex items-center justify-between rounded-2xl px-5 py-5 bg-white/10 hover:bg-white/15 border border-white/20 text-white transition">
              <div className="flex items-center gap-3">
                <div className="grid place-items-center rounded-xl bg-white/20 w-10 h-10"><Play /></div>
                <div className="text-lg font-semibold">Go to Live Feed</div>
              </div>
            </Link>

            <Link to="/alerts" className="flex items-center justify-between rounded-2xl px-5 py-5 bg-white/10 hover:bg-white/15 border border-white/20 text-white transition">
              <div className="flex items-center gap-3">
                <div className="grid place-items-center rounded-xl bg-white/20 w-10 h-10"><Bell /></div>
                <div className="text-lg font-semibold">View Alerts</div>
              </div>
            </Link>

            <Link to="/settings" className="flex items-center justify-between rounded-2xl px-5 py-5 bg-white/10 hover:bg-white/15 border border-white/20 text-white transition">
              <div className="flex items-center gap-3">
                <div className="grid place-items-center rounded-xl bg-white/20 w-10 h-10"><Settings /></div>
                <div className="text-lg font-semibold">Settings</div>
              </div>
            </Link>
          </div>
        </Card>

        <SystemToggle className="mt-4" />
        <SirenToggle className="mt-4" />
      </div>
    </div>
  )
}
