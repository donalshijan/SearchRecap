import React, { useState, useEffect } from 'react'
import Chart from '../components/Chart'
import TimeframeSelector from '../components/TimeframeSelector'
import { fetchAnalytics } from '../api/analytics'

export default function Dashboard() {
  const [period, setPeriod] = useState('day')
  const [data, setData] = useState([])

  useEffect(() => {
    fetchAnalytics(period).then(res => {
      const dataArray = Object.entries(res.category_distribution || {}).map(
        ([category, num_of_search_queries]) => ({
          category,
          value: num_of_search_queries
        })
      )
      setData(dataArray)
    }).catch(err => console.error("Failed to fetch analytics:", err))
  }, [period])

  return (
    <div className="dashboard-container">
      <TimeframeSelector selected={period} onChange={setPeriod} />
      <div className="chart-wrapper">
        <Chart data={data} />
      </div>
    </div>
  )
}
