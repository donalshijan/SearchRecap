import React, { useEffect } from "react";
// eslint-disable-next-line no-unused-vars
import { motion, AnimatePresence, useMotionValue, useTransform, animate } from "framer-motion";
import { useFlashcards } from "../hooks/useFlashcards";

export default function Flashcards() {
  const {
    currentCategory,
    switchCategory,
    nextQuery,
    prevQuery,
    currentQuery,
    loading,
    fetchBatch,
    getProgress,
  } = useFlashcards();

  const { index, total, hasLooped, maxClockWiseCursor, minAntiClockWiseCursor } = getProgress();
  const progressClockwise = Math.max(0, maxClockWiseCursor) / Math.max(total-1,1);
  const progressAntiClockwise = Math.abs(Math.min(0, minAntiClockWiseCursor)) / Math.max(total-1,1);
  // const progressClockwise = Math.max(0, maxClockWiseCursor+1) / (total || 1);
  // const progressAntiClockwise = Math.abs(Math.min(0, minAntiClockWiseCursor)) / (total || 1);
  const circumference = 2 * Math.PI * 45; // r = 45

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


  // angle MV: start angle (radians). Subtract PI/2 so 0 => 12 o'clock
  const startAngle = ( (index ) / Math.max(total-1,1)) * 2 * Math.PI - Math.PI / 2;
  const angle = useMotionValue(startAngle);

  // animate angle whenever index or total changes (smooth orbit)
  useEffect(() => {
    const newAngle = ( (index ) / Math.max(total-1,1)) * 2 * Math.PI - Math.PI / 2;
    // small delta -> animate, huge wrap -> snap
    const delta = Math.abs(newAngle - angle.get());
    if (Math.abs(delta - 2 * Math.PI) < 0.0001) {
      angle.set(newAngle);
    } else {
      animate(angle, newAngle, { duration: 0.4, ease: "easeInOut" });
    }
  }, [index, total, angle]);


  useEffect(() => {
    switchCategory(currentCategory);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

    // derive pointer X/Y as motion values (in the same 0..100 svg coordinate space)
  const pointerX = useTransform(angle, (a) => 50 + 45 * Math.cos(a));
  const pointerY = useTransform(angle, (a) => 50 + 45 * Math.sin(a));

  return (
    <div className="flashcards-container ">

      <div className="category-selector">
        <label htmlFor="category">Category:</label>
        <select id="category" value={currentCategory} onChange={(e) => switchCategory(e.target.value)}>
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
            key={currentQuery() || "empty"}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="flashcard"
          >
            {loading ? "Loading..." : currentQuery() || "No cards yet"}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Circular Dial Navigation */}
      <div className="navigation-dial">
        <button
          onClick={prevQuery}
          disabled={loading}
          className="next-button"
        >
          ←
        </button>
        {/* SVG Circular Track */}
            <div className="dial-center">
                <svg viewBox="0 0 100 100" className="dial-svg" role="img" aria-hidden="true" >
                  {/* Base circle */}
                  <circle
                      className="dial-bg"
                      cx="50%"
                      cy="50%"
                      r="45"
                      strokeWidth="6"
                      fill="none"
                  />
                  {/* Progress arc */}
                  <motion.circle
                      className="dial-progress clockwise"
                      cx="50%"
                      cy="50%"
                      r="45"
                      strokeWidth="6"
                      fill="none"
                      strokeDasharray={`${circumference} ${circumference}`}
                      strokeDashoffset={circumference * (1 - progressClockwise)}
                      strokeLinecap="round"
                      animate={{ strokeDashoffset: circumference * (1 - progressClockwise) }}
                      transition={{ duration: 0.4, ease: "easeInOut" }}
                      style={{
                        transformOrigin: "50% 50%",
                        transform: "rotate(-90deg)" // keep starting point at 12 o'clock
                      }}
                  />
                  <motion.circle
                    className="dial-progress anticlockwise"
                    cx="50%"
                    cy="50%"
                    r="45"
                    strokeWidth="6"
                    fill="none"
                    strokeDasharray={`${circumference} ${circumference}`}
                    strokeDashoffset={circumference * (1 - progressAntiClockwise)}
                    strokeLinecap="round"
                    animate={{ strokeDashoffset: circumference * (1 - progressAntiClockwise) }}
                    transition={{ duration: 0.4, ease: "easeInOut" }}
                    style={{
                      transformOrigin: "50% 50%",
                      transform: "rotate(90deg) scale(-1,1)" // mirror horizontally, start from same top
                    }}
                  />
                  <motion.circle
                    className="dial-pointer"
                    cx={pointerX}
                    cy={pointerY}
                    r="3.5"
                    fill="var(--accent, #00b7ff)"
                    stroke="none"
                    // optional subtle animation on scale when moving
                    animate={{ scale: [1, 1.15, 1] }}
                    transition={{ duration: 0.4, repeat: 0, ease: "easeInOut" }}
                  />
                </svg>

                {/* Overlay button for new batch */}
                <AnimatePresence>
                {hasLooped && (
                    <motion.button
                    key="next-batch"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 ,scale: 0.95 }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    onClick={async () => await fetchBatch(currentCategory)}
                    disabled={loading}
                    className="next-batch-button"
                    >
                    🔄 Fetch Next Batch
                    </motion.button>
                )}
                </AnimatePresence>
            </div>

        {/* Prev / Next buttons */}
        <button
          onClick={nextQuery}
          disabled={loading}
          className="next-button"
        >
          →
        </button>
      </div>

      {/* Textual progress fallback */}
      {total > 0 && (
        <p className="progress-text">
          Card {index + 1} / {total}
        </p>
      )}
    </div>
  );
}