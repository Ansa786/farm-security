import { create } from 'zustand'

// small persisted helper
const persisted = (key, initial) => {
  let start = initial
  try {
    const raw = localStorage.getItem(key)
    if (raw) start = JSON.parse(raw)
  } catch {}
  return create((set) => ({
    ...start,
    _save: (obj) =>
      set((s) => {
        const ns = { ...s, ...obj }
        localStorage.setItem(key, JSON.stringify(ns))
        return ns
      }),
  }))
}

export const useSettings = persisted('settings', {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  streamUrl: import.meta.env.VITE_STREAM_URL || '',
  mock: (import.meta.env.VITE_USE_MOCK || 'true').toLowerCase() === 'true',
  bgUrl:
    import.meta.env.VITE_BG_URL ||
    'https://images.unsplash.com/photo-1469474968028-56623f02e42e?q=80&w=1600&auto=format&fit=crop',
})

export const useSystem = persisted('system', { enabled: true })

export const useUI = create((set) => ({
  sidebarOpen: false,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  openSidebar: () => set({ sidebarOpen: true }),
  closeSidebar: () => set({ sidebarOpen: false }),
}))
