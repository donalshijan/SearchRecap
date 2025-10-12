import React, { useState, useEffect } from 'react'
import Tabs from './components/Tabs'
import Dashboard from './pages/Dashboard'
import Flashcards from './pages/Flashcards'
import { FlashcardProvider } from "./contexts/FlashcardContext";
import ThemeToggle from './components/ThemeToggle'

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const renderTab = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />
      case 'flashcards':
        return (
          <FlashcardProvider>
            <Flashcards />
          </FlashcardProvider>
        )
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="app-container">
      <header className="header">
        <Tabs active={activeTab} onChange={setActiveTab} />
        <ThemeToggle theme={theme} setTheme={setTheme} />
      </header>
      <main className="main-content">
        {renderTab()}
      </main>
    </div>
  )
}
