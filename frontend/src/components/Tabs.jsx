import React from 'react'

export default function Tabs({ active, onChange }) {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'flashcards', label: 'Flashcards' },
  ]

  return (
    <nav className="tabs">
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`tab-button ${active === tab.id ? 'active' : ''}`}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  )
}
