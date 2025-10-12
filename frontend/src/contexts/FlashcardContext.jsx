// src/contexts/FlashcardContext.jsx
import React, { createContext, useState } from 'react'
import axios from 'axios'

const FlashcardContext = createContext(null)

export function FlashcardProvider({ children }) {
  const [cache, setCache] = useState({}) // { category: { batch: [], cursor: 0 } }
  const [currentCategory, setCurrentCategory] = useState('Lexis')
  const [loading, setLoading] = useState(false)
  const LIMIT = 2

  const fetchBatch = async (category, forceRefresh = false) => {
    setLoading(true)
    try {
      const res = await axios.get('http://192.168.1.88:8000/random-query', {
        params: { category, limit: LIMIT, force_refresh: forceRefresh }
      })
      // backend returns an array of queries (adjust if your backend returns different shape)
      const newBatch = Array.isArray(res.data) ? res.data : (res.data.queries ?? [])
      setCache(prev => ({ ...prev, [category]: { batch: newBatch, cursor: 0 } }))
    } catch (err) {
      console.error('fetchBatch error', err)
    } finally {
      setLoading(false)
    }
  }

  const nextQuery = async () => {
    const cat = currentCategory
    const entry = cache[cat]

    // If no cached batch, fetch one
    if (!entry || !entry.batch || entry.batch.length === 0  || entry.cursor >= entry.batch.length) {
      await fetchBatch(cat)
      return
    }

    const { batch, cursor } = entry

    // If cursor already beyond last index => we've consumed whole batch; fetch next on next call
    if (cursor < batch.length - 1) {
      // mark as consumed by setting cursor to batch.length (so nextQuery triggers fetchBatch above)
      setCache(prev => ({ ...prev, [cat]: { ...entry, cursor: batch.length } }))
      return
    }

    // Otherwise advance cursor
    setCache(prev => ({ ...prev, [cat]: { ...entry, cursor: cursor + 1 } }))
  }

  const currentQuery = () => {
    const entry = cache[currentCategory]
    if (!entry || !entry.batch || entry.batch.length === 0) return null
    const idx = Math.min(entry.cursor, entry.batch.length - 1)
    return entry.batch[idx]
  }

  const switchCategory = async (category) => {
    setCurrentCategory(category)
    if (!cache[category] || !cache[category].batch || cache[category].batch.length === 0) {
      await fetchBatch(category)
    }
  }

  return (
    <FlashcardContext.Provider value={{
      cache,
      currentCategory,
      switchCategory,
      nextQuery,
      currentQuery,
      loading,
      fetchBatch
    }}>
      {children}
    </FlashcardContext.Provider>
  )
}

export default FlashcardContext
