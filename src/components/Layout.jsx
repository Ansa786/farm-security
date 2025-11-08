import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Bell, Camera, Gauge, Settings as Cog, Menu, LogOut } from 'lucide-react'
import classNames from 'classnames'
import { useSettings, useUI } from '../store/useStore'

const NavItem = ({ to, icon: Icon, label, onClick }) => {
  const { pathname } = useLocation()
  const active = pathname === to
  return (
    <Link to={to} onClick={onClick} className={classNames('flex items-center gap-3 rounded-xl px-3 py-2 transition', active ? 'bg-gray-900 text-white' : 'text-gray-100/90 hover:bg-white/10')} title={label}>
      <Icon size={18} />
      <span className="font-medium">{label}</span>
    </Link>
  )
}

export default function Layout({ children }) {
  const { bgUrl } = useSettings()
  const nav = useNavigate()
  const { sidebarOpen, toggleSidebar, closeSidebar } = useUI()

  const Sidebar = (
    <aside className={classNames('fixed left-0 top-0 h-full w-[280px] transition-transform duration-300', sidebarOpen ? 'translate-x-0' : '-translate-x-full', 'z-40')}>
      <div className="h-full bg-black/60 backdrop-blur-md border-r border-white/10 p-5 flex flex-col">
        <div className="mb-4">
          <h1 className="text-xl font-bold text-white">Intrusion Alert</h1>
          <p className="text-xs text-white/70">AI + IoT Security</p>
        </div>

        <nav className="grid gap-2 flex-1">
          <NavItem to="/dashboard" icon={Gauge} label="Dashboard" onClick={closeSidebar} />
          <NavItem to="/live" icon={Camera} label="Live Feed" onClick={closeSidebar} />
          <NavItem to="/alerts" icon={Bell} label="Alerts" onClick={closeSidebar} />
          <NavItem to="/settings" icon={Cog} label="Settings" onClick={closeSidebar} />
        </nav>

        <button onClick={()=>nav('/')} className="rounded-2xl border border-white/15 bg-white/5 hover:bg-white/10 px-3 py-2 flex items-center gap-2 text-sm text-white">
          <LogOut size={16}/> Home
        </button>
      </div>
    </aside>
  )

  const Overlay = sidebarOpen ? <div className="fixed inset-0 z-30 bg-black/40 lg:hidden" onClick={closeSidebar} aria-hidden="true" /> : null

  return (
    <div className="min-h-screen w-full relative text-white">
      <div className="fixed inset-0 -z-10 bg-cover bg-center" style={{ backgroundImage: `url(${bgUrl})` }} />
      <div className="fixed inset-0 -z-10 bg-black/25" />

      {Sidebar}
      {Overlay}

      <header className="sticky top-0 z-20 px-4 py-3 lg:px-6">
        <button onClick={toggleSidebar} className="rounded-xl bg-black/60 hover:bg-black/70 border border-white/10 p-2 backdrop-blur-md" aria-label="Toggle menu" title="Menu">
          <Menu size={20} />
        </button>
      </header>

      <main className="px-4 pb-8 lg:px-8">
        <div className="mx-auto max-w-5xl">{children}</div>
      </main>
    </div>
  )
}
