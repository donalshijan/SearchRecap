
import { getBackendUrl } from '../config.js'

export async function fetchAnalytics(period = 'day') {
  try {
    const backendUrl = getBackendUrl()
    if (!backendUrl) {
      throw new Error('Backend URL not configured')
    }
    const res = await fetch(`${backendUrl}/analytics?period=${period}`)
    if (!res.ok) throw new Error(`Failed to fetch analytics: ${res.status}`)
    return await res.json()
  } catch (err) {
    console.error(err)
    return []
  }
}
