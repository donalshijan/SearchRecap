export async function fetchAnalytics(period = 'day') {
  try {
    const res = await fetch(`http://192.168.1.88:8000/analytics?period=${period}`)
    if (!res.ok) throw new Error(`Failed to fetch analytics: ${res.status}`)
    return await res.json()
  } catch (err) {
    console.error(err)
    return []
  }
}
