"use client";

import { motion , AnimatePresence } from "framer-motion";
import { useState, useRef } from "react";

interface Option {
  id: number;
  text: string;
  order: number;
}

interface OptionButtonProps {
  option: Option;
  index: number;
  isSelected: boolean;
  isJustAnswered: boolean;
  onClick: () => void;
}

export default function OptionButton({
  option,
  index,
  isSelected,
  isJustAnswered,
  onClick,
}: OptionButtonProps) {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!buttonRef.current) return;
    const rect = buttonRef.current.getBoundingClientRect();
    setMousePos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  const letter = String.fromCharCode(65 + index);

  return (
    <motion.button
      ref={buttonRef}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      variants={{
        hidden: { opacity: 0, y: 20, scale: 0.95 },
        visible: {
          opacity: 1,
          y: 0,
          scale: 1,
          transition: { type: "spring", stiffness: 300, damping: 20 },
        },
      }}
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      className={`group relative w-full flex items-center gap-4 p-4 rounded-xl border-2 transition-all overflow-hidden text-left ${
        isSelected
          ? "border-emerald-500 bg-gradient-to-br from-emerald-50 to-teal-50 shadow-lg"
          : "border-slate-200 hover:border-slate-300 bg-white"
      }`}
    >
      {/* Spotlight effect */}
      {isHovered && !isSelected && (
        <div
          className="absolute pointer-events-none opacity-60"
          style={{
            left: mousePos.x - 100,
            top: mousePos.y - 100,
            width: 200,
            height: 200,
            background: "radial-gradient(circle, rgba(249,115,22,0.15), transparent 70%)",
          }}
        />
      )}

      {/* Letter badge */}
      <motion.div
        animate={{
          scale: isSelected ? [1, 1.3, 1] : 1,
          rotate: isSelected ? [0, -10, 10, 0] : 0,
        }}
        transition={{ duration: 0.4, type: "spring" }}
        className={`relative flex-shrink-0 w-11 h-11 rounded-xl flex items-center justify-center font-bold text-base transition-all ${
          isSelected
            ? "bg-gradient-to-br from-emerald-500 to-teal-500 text-white shadow-lg"
            : "bg-slate-100 text-slate-700 group-hover:bg-slate-200"
        }`}
      >
        {letter}

        {/* Confetti particles on selection */}
        {isJustAnswered &&
          Array.from({ length: 8 }).map((_, i) => (
            <motion.span
              key={i}
              initial={{ scale: 0, x: 0, y: 0 }}
              animate={{
                scale: [0, 1, 0],
                x: Math.cos((i * Math.PI) / 4) * 30,
                y: Math.sin((i * Math.PI) / 4) * 30,
              }}
              transition={{ duration: 0.6 }}
              className="absolute w-1.5 h-1.5 rounded-full bg-emerald-500"
            />
          ))}
      </motion.div>

      {/* Option text */}
      <span
        className={`flex-1 text-sm md:text-base transition-colors ${
          isSelected ? "text-emerald-900 font-semibold" : "text-slate-800"
        }`}
      >
        {option.text}
      </span>

      {/* Checkmark */}
      <AnimatePresence>
        {isSelected && (
          <motion.div
            initial={{ scale: 0, rotate: -90 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0, rotate: 90 }}
            transition={{ type: "spring", stiffness: 300, damping: 15 }}
            className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center shadow-lg"
          >
            <motion.svg
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.3, delay: 0.1 }}
              className="w-5 h-5 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              strokeWidth={3}
            >
              <motion.path
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 0.3, delay: 0.1 }}
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M5 13l4 4L19 7"
              />
            </motion.svg>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  );
}