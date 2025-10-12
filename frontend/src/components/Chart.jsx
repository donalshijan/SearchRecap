import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function Chart({ data }) {
  const safeData = Array.isArray(data) ? data : []
  
  if (!safeData || safeData.length === 0) {
    return <p>No data available</p>
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={safeData} margin={{ top: 20, right: 30, bottom: 10, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="category" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  )
}
