// src/contexts/FlashcardContext.jsx
import React, { createContext, useState } from 'react'
import axios from 'axios'
import { useConfig } from "../hooks/useConfig";

const FlashcardContext = createContext(null)

export function FlashcardProvider({ children }) {
  const [cache, setCache] = useState({}) // { category: { batch: [], entryIdx: 0, hasLooped: false } }
  const [currentCategory, setCurrentCategory] = useState('Lexis')
  const [loading, setLoading] = useState(false)
  const { backendUrl } = useConfig();
  const LIMIT = 10

  const fetchBatch = async (category, forceRefresh = false) => {
    if (!backendUrl) {
      console.error('Backend URL not configured')
      setLoading(false)
      return
    }
    setLoading(true)
    try {
      const res = await axios.get(`${backendUrl}/random-query`, {
        params: { category, limit: LIMIT, force_refresh: forceRefresh }
      })
      const newBatch = Array.isArray(res.data) ? res.data : (res.data.queries ?? [])
      setCache(prev => ({
        ...prev,
        [category]: { batch: newBatch, entryIdx: 0, hasLooped: false , maxClockWiseCursor : 0, minAntiClockWiseCursor : 0, cursor : 0 }
      }))
    } catch (err) {
      console.error('fetchBatch error', err)
    } finally {
      setLoading(false)
    }
  }

  // 🚀 Move forward circularly
  const nextQuery = () => {
    const cat = currentCategory
    const entry = cache[cat]
    if (!entry || !entry.batch || entry.batch.length === 0) return

    const hasLooped = Math.max(entry.maxClockWiseCursor,entry.cursor + 1) + -1*entry.minAntiClockWiseCursor == entry.batch.length-1 ? true : entry.hasLooped
    let newMaxClockWiseCursor = entry.maxClockWiseCursor
    if(entry.cursor>=0){
      newMaxClockWiseCursor = Math.max(entry.maxClockWiseCursor,Math.min(entry.batch.length-1,entry.cursor + 1))
    }
    const nextEntryIdx = (entry.entryIdx + 1) % entry.batch.length

    setCache(prev => ({
      ...prev,
      [cat]: { ...entry, entryIdx: nextEntryIdx, hasLooped , maxClockWiseCursor : newMaxClockWiseCursor , cursor : Math.min(entry.batch.length-1,entry.cursor + 1)}
    }))
  }

  // ⬅️ Move backward circularly
  const prevQuery = () => {
    const cat = currentCategory
    const entry = cache[cat]
    if (!entry || !entry.batch || entry.batch.length === 0) return

    const hasLooped = entry.maxClockWiseCursor + -1*Math.min(entry.minAntiClockWiseCursor,entry.cursor - 1 ) == entry.batch.length-1 ? true : entry.hasLooped
    let newMinAntiClockWiseCursor = entry.minAntiClockWiseCursor
    if(entry.cursor<=0){
      newMinAntiClockWiseCursor = Math.min(entry.minAntiClockWiseCursor,Math.max(-1*(entry.batch.length-1),entry.cursor -1) )
    }
    const prevEntryIdx = (entry.entryIdx - 1 + entry.batch.length) % entry.batch.length
    setCache(prev => ({
      ...prev,
      [cat]: { ...entry, entryIdx: prevEntryIdx , minAntiClockWiseCursor : newMinAntiClockWiseCursor , cursor : Math.max(-1*(entry.batch.length-1),entry.cursor -1), hasLooped}
    }))
  }

  const currentQuery = () => {
    const entry = cache[currentCategory]
    if (!entry || !entry.batch || entry.batch.length === 0) return null
    return entry.batch[entry.entryIdx]
  }

  const switchCategory = async (category) => {
    setCurrentCategory(category)
    if (!cache[category] || !cache[category].batch || cache[category].batch.length === 0) {
      await fetchBatch(category)
    }
  }

  const getProgress = () => {
    const entry = cache[currentCategory]
    if (!entry || !entry.batch || entry.batch.length === 0) return { index: 0, total: 0 }
    return { index: entry.entryIdx, total: entry.batch.length, hasLooped: entry.hasLooped ,maxClockWiseCursor : entry.maxClockWiseCursor, minAntiClockWiseCursor: entry.minAntiClockWiseCursor}
  }

  return (
    <FlashcardContext.Provider value={{
      cache,
      currentCategory,
      switchCategory,
      nextQuery,
      prevQuery,
      currentQuery,
      loading,
      fetchBatch,
      getProgress
    }}>
      {children}
    </FlashcardContext.Provider>
  )
}

export default FlashcardContext
