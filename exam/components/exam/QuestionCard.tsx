"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import OptionButton from "./OptionButton";

interface Option {
  id: number;
  text: string;
  order: number;
}

interface Item {
  id: number;
  item_type: string;
  title: string;
  instruction?: string;
  question_text?: string;
  max_score: number;
  order: number;
  options: Option[];
}

interface QuestionCardProps {
  item: Item;
  itemIndex: number;
  totalItems: number;
  selectedOptions: number[];
  onSelectOption: (itemId: number, optionId: number) => void;
  isSaving: boolean;
}

export default function QuestionCard({
  item,
  itemIndex,
  totalItems,
  selectedOptions,
  onSelectOption,
  isSaving,
}: QuestionCardProps) {
  const [justAnswered, setJustAnswered] = useState<number | null>(null);

  const handleSelect = (optionId: number) => {
    setJustAnswered(optionId);
    onSelectOption(item.id, optionId);
    setTimeout(() => setJustAnswered(null), 800);
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={item.id}
        initial={{ opacity: 0, x: 30, filter: "blur(10px)" }}
        animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
        exit={{ opacity: 0, x: -30, filter: "blur(10px)" }}
        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
        className="relative overflow-hidden rounded-2xl bg-white/80 backdrop-blur-xl border border-slate-200 shadow-xl p-6 md:p-8"
      >
        {/* Decorative corner */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-orange-500/10 to-rose-500/10 rounded-full blur-2xl pointer-events-none" />

        <div className="relative">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ type: "spring", stiffness: 200, damping: 15 }}
                className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-rose-500 flex items-center justify-center text-white font-bold text-lg shadow-lg"
              >
                {itemIndex + 1}
              </motion.div>
              <div>
                <div className="text-xs uppercase tracking-widest text-slate-400 font-semibold">
                  Question {itemIndex + 1} of {totalItems}
                </div>
                <div className="text-xs text-slate-500">
                  Max score: {item.max_score}
                </div>
              </div>
            </div>

            {isSaving && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-2 text-xs text-slate-400"
              >
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                Saving...
              </motion.div>
            )}
          </div>

          {/* Question text */}
          <motion.h3
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xl md:text-2xl font-bold text-slate-900 mb-6 leading-snug"
          >
            {item.question_text || item.title}
          </motion.h3>

          {/* Options */}
          {item.options.length > 0 ? (
            <motion.div
              initial="hidden"
              animate="visible"
              variants={{
                hidden: {},
                visible: { transition: { staggerChildren: 0.08 } },
              }}
              className="space-y-3"
            >
              {item.options.map((option, idx) => (
                <OptionButton
                  key={option.id}
                  option={option}
                  index={idx}
                  isSelected={selectedOptions.includes(option.id)}
                  isJustAnswered={justAnswered === option.id}
                  onClick={() => handleSelect(option.id)}
                />
              ))}
            </motion.div>
          ) : (
            <div className="text-center py-8 text-slate-400">
              No options available for this question
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}