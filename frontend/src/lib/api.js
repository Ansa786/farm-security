import axios from 'axios'
import { useSettings, useSystem } from '../store/useStore'

export function getClient() {
  const { apiBaseUrl } = useSettings.getState()
  return axios.create({ baseURL: apiBaseUrl, timeout: 10000 })
}

export async function fetchAlerts() {
  const { mock } = useSettings.getState()
  if (mock) {
    const res = await fetch('/mock/alerts.json')
    return await res.json()
  }
  try {
    const { data } = await getClient().get('/alerts')
    return data || []
  } catch (error) {
    console.error('Failed to fetch alerts:', error)
    return []
  }
}

export async function setSystemEnabled(flag) {
  const { mock } = useSettings.getState()
  useSystem.getState()._save({ enabled: flag })
  if (!mock) {
    try {
      await getClient().post('/system', { enabled: flag })
    } catch (error) {
      console.error('Failed to set system state:', error)
    }
  }
  return { ok: true }
}

export async function getSystemStatus() {
  const { mock } = useSettings.getState()
  if (mock) {
    return { status: 'ON', message: 'System is active.', siren_state: 'OFF' }
  }
  try {
    const { data } = await getClient().get('/api/system/status')
    return data
  } catch (error) {
    console.error('Failed to fetch system status:', error)
    return { status: 'UNKNOWN', message: 'Failed to fetch status', siren_state: 'UNKNOWN' }
  }
}

export async function toggleSiren(action) {
  const { mock } = useSettings.getState()
  if (mock) {
    return { success: true, siren_state: action, message: `Siren turned ${action}` }
  }
  try {
    const { data } = await getClient().post('/api/system/siren/toggle', { action })
    return data
  } catch (error) {
    console.error('Failed to toggle siren:', error)
    return { success: false, message: 'Failed to toggle siren' }
  }
}

export async function getCameraStatus() {
  const { mock } = useSettings.getState()
  if (mock) {
    return { status: 'streaming', url: 'http://192.168.43.77/', system_active: true }
  }
  try {
    const { data } = await getClient().get('/camera/status')
    return data
  } catch (error) {
    console.error('Failed to fetch camera status:', error)
    return { status: 'disconnected', url: '', system_active: false }
  }
}

export function getLiveFeedUrl() {
  const { apiBaseUrl, mock, streamUrl } = useSettings.getState()
  if (mock || !apiBaseUrl) {
    // Fallback to direct stream URL if mock or no API URL
    return streamUrl || ''
  }
  // Use backend's live feed endpoint
  return `${apiBaseUrl}/camera/live_feed`
}
