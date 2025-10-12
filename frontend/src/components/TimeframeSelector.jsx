import React from 'react'

export default function TimeframeSelector({ selected, onChange }) {
  const options = ['day', 'week', 'month', 'year']

  return (
    <div className="timeframe-selector">
      {options.map(opt => (
        <button
          key={opt}
          onClick={() => onChange(opt)}
          className={`timeframe-btn ${selected === opt ? 'selected' : ''}`}
        >
          {opt.charAt(0).toUpperCase() + opt.slice(1)}
        </button>
      ))}
    </div>
  )
}
