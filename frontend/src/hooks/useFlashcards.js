// src/hooks/useFlashcards.js
import { useContext } from 'react'
import FlashcardContext from '../contexts/FlashcardContext'

export function useFlashcards() {
  const ctx = useContext(FlashcardContext)
  if (!ctx) {
    throw new Error('useFlashcards must be used within a FlashcardProvider')
  }
  return ctx
}
