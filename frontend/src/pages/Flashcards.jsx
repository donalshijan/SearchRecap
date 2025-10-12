import React, { useEffect } from "react";
// eslint-disable-next-line no-unused-vars
import { motion, AnimatePresence } from "framer-motion"; // for smooth transitions
import { useFlashcards } from "../hooks/useFlashcards";

export default function Flashcards() {
  const {
    currentCategory,
    switchCategory,
    nextQuery,
    currentQuery,
    loading,
  } = useFlashcards();

  const categories = [
    "Lexis",
    "History",
    "Biography",
    "Science",
    "Technology",
    "Culture",
    "Society",
    "Health",
    "Miscellaneous",
  ];

  useEffect(() => {
    switchCategory(currentCategory);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flashcards-container">
      <h2 className="section-title">Flashcards</h2>

      <div className="category-selector">
        <label htmlFor="category">Category:</label>
        <select
          id="category"
          value={currentCategory}
          onChange={(e) => switchCategory(e.target.value)}
        >
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      <div className="flashcard-box">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQuery()}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="flashcard"
          >
            {loading ? "Loading..." : currentQuery()}
          </motion.div>
        </AnimatePresence>
      </div>

      <button
        onClick={nextQuery}
        disabled={loading}
        className="next-button"
      >
        Next →
      </button>
    </div>
  );
}