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
  const { data } = await getClient().get('/alerts')
  return data
}

export async function setSystemEnabled(flag) {
  const { mock } = useSettings.getState()
  useSystem.getState()._save({ enabled: flag })
  if (!mock) {
    try {
      await getClient().post('/system', { enabled: flag })
    } catch {}
  }
  return { ok: true }
}
