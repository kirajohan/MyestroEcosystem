"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLanguage } from "@/app/providers";

interface WritingEditorProps {
  itemId: number;
  initialValue: string;
  onSave: (itemId: number, text: string) => void;
  minWords?: number;
  maxWords?: number;
  isSaving: boolean;
  title?: string;
  instruction?: string;
}

export default function WritingEditor({
  itemId,
  initialValue,
  onSave,
  minWords = 0,
  maxWords = 500,
  isSaving,
  title,
  instruction,
}: WritingEditorProps) {
  const { t } = useLanguage();
  const [text, setText] = useState(initialValue);
  const [focusMode, setFocusMode] = useState(false);
  const [pasteWarning, setPasteWarning] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const [particles, setParticles] = useState<{ id: number; x: number; y: number }[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const particleIdRef = useRef(0);
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Sync initialValue when item changes
  // (faqat item almashganda — aks holda saqlash tugagach yangi yozilgan matn eskisiga qaytib ketadi)
  useEffect(() => {
    setText(initialValue);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itemId]);

  // ── Word count ──────────────────────────────────────
  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
  const charCount = text.length;

  // ── Target ring progress ────────────────────────────
  const targetMin = minWords || 150;
//   const targetMax = maxWords || 300;
  const progress = Math.min(1, wordCount / targetMin);
  const reachedMin = wordCount >= targetMin;
  const exceededMax = maxWords > 0 && wordCount > maxWords;

  // Ring SVG params
  const ringSize = 80;
  const strokeWidth = 6;
  const radius = (ringSize - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference * (1 - Math.min(1, progress));

  const ringColor = exceededMax
    ? "#ef4444"
    : reachedMin
    ? "#10b981"
    : "#f97316";

  // ── Autosave (debounced 800ms) ──────────────────────
  useEffect(() => {
    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    saveTimeoutRef.current = setTimeout(() => {
      if (text !== initialValue) {
        onSave(itemId, text);
      }
    }, 800);
    return () => {
      if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    };
  }, [text, itemId, onSave, initialValue]);

  // ── Flush: kutilayotgan matnni darhol saqlash (blur / unmount) ──
  const latestRef = useRef({ text, initialValue, itemId, onSave });
  latestRef.current = { text, initialValue, itemId, onSave };

  const flushSave = useCallback(() => {
    const { text: txt, initialValue: iv, itemId: id, onSave: save } = latestRef.current;
    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    if (txt !== iv) save(id, txt);
  }, []);

  // Block/item almashganda yoki sahifadan chiqilganda yo'qolmasligi uchun
  useEffect(() => () => flushSave(), [itemId, flushSave]);

  // ── Paste blocker ───────────────────────────────────
  // TEST: paste ruxsat etilgan. Qayta bloklash uchun true qiling.
  const BLOCK_PASTE = false;
  const handlePaste = useCallback((e: React.ClipboardEvent) => {
    if (!BLOCK_PASTE) return;
    e.preventDefault();
    setPasteWarning(true);
    setTimeout(() => setPasteWarning(false), 2500);

    // Optional: allow plain text paste without formatting
    // const plainText = e.clipboardData.getData("text/plain");
    // document.execCommand("insertText", false, plainText);
  }, []);

  // ── Typewriter particles ────────────────────────────
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Skip modifier keys
    if (e.ctrlKey || e.metaKey || e.altKey || e.shiftKey) return;
    if (e.key.length !== 1) return; // non-character keys

    const rect = textareaRef.current?.getBoundingClientRect();
    if (!rect) return;

    const id = ++particleIdRef.current;
    const x = Math.random() * rect.width;
    const y = rect.height - 10;

    setParticles((prev) => [...prev, { id, x, y }]);
    setTimeout(() => {
      setParticles((prev) => prev.filter((p) => p.id !== id));
    }, 800);
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };

  return (
    <>
      {/* ═══ FOCUS MODE OVERLAY ═══ */}
      <AnimatePresence>
        {focusMode && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-slate-950/90 backdrop-blur-xl"
          />
        )}
      </AnimatePresence>

      {/* ═══ MAIN EDITOR CONTAINER ═══ */}
      <div
        className={`relative transition-all duration-500 ease-[cubic-bezier(0.22,1,0.36,1)] ${
          focusMode
            ? "fixed inset-x-0 top-0 bottom-0 z-50 flex items-center justify-center p-4 md:p-12"
            : "relative"
        }`}
      >
        <div
          className={`relative overflow-hidden rounded-2xl transition-all duration-500 ${
            focusMode ? "max-w-3xl w-full h-full" : "w-full"
          } ${
            isFocused && !focusMode
              ? "shadow-2xl ring-2 ring-violet-400/50"
              : "shadow-xl"
          } ${
            focusMode
              ? "bg-slate-900/95 border border-white/10"
              : "bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border border-slate-200/60 dark:border-slate-700/60"
          }`}
          style={
            isFocused && !focusMode
              ? {
                  boxShadow:
                    "0 0 40px rgba(139, 92, 246, 0.3), 0 0 80px rgba(244, 114, 182, 0.2)",
                }
              : undefined
          }
        >
          {/* ── Glowing active border (animated) ── */}
          {isFocused && !focusMode && (
            <div className="absolute inset-0 rounded-2xl pointer-events-none">
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-violet-500/20 via-fuchsia-500/20 to-indigo-500/20 animate-pulse" />
            </div>
          )}

          {/* ── Header ── */}
          <div
            className={`flex items-center justify-between gap-3 px-5 py-3 border-b ${
              focusMode ? "border-white/10" : "border-slate-200/60 dark:border-slate-700/60"
            }`}
          >
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <div className="text-2xl flex-shrink-0">✍️</div>
              <div className="min-w-0 flex-1">
                <h3
                  className={`text-xs font-bold uppercase tracking-widest truncate ${
                    focusMode ? "text-orange-400" : "text-orange-600 dark:text-orange-400"
                  }`}
                >
                  {title || t("write.title_default")}
                </h3>
                {instruction && !focusMode && (
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate mt-0.5">
                    {instruction}
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2 flex-shrink-0">
              {/* Focus mode toggle */}
              <button
                onClick={() => setFocusMode((v) => !v)}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors ${
                  focusMode
                    ? "bg-orange-500 text-white"
                    : focusMode
                    ? "text-slate-300 hover:bg-white/10"
                    : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                }`}
                title={t("write.focus_title")}
              >
                {focusMode ? t("write.exit") : t("write.focus")}
              </button>
            </div>
          </div>

          {/* ── Main editing area ── */}
          <div
            className={`relative ${
              focusMode ? "flex-1 flex flex-col" : ""
            }`}
          >
            {/* Paste warning */}
            <AnimatePresence>
              {pasteWarning && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute top-2 left-1/2 -translate-x-1/2 z-20 bg-amber-500 text-white text-xs font-semibold px-3 py-1.5 rounded-full shadow-lg"
                >
                  {t("write.paste_blocked")}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Textarea */}
            <div className="relative">
              <textarea
                ref={textareaRef}
                value={text}
                onChange={handleChange}
                onPaste={handlePaste}
                onFocus={() => setIsFocused(true)}
                onBlur={() => {
                  setIsFocused(false);
                  flushSave();
                }}
                onKeyDown={handleKeyDown}
                placeholder={t("write.placeholder")}
                className={`w-full resize-none outline-none transition-colors ${
                  focusMode
                    ? "bg-transparent text-slate-100 placeholder-slate-600"
                    : "bg-transparent text-slate-800 dark:text-slate-100 placeholder-slate-400"
                } ${focusMode ? "text-lg leading-relaxed" : "text-base"}`}
                style={{
                  minHeight: focusMode ? "60vh" : "300px",
                  padding: focusMode ? "2rem" : "1.5rem",
                  fontFamily: focusMode
                    ? "'Georgia', serif"
                    : "inherit",
                }}
                spellCheck
              />

              {/* Typewriter particles */}
              <div className="absolute inset-0 pointer-events-none overflow-hidden">
                {particles.map((p) => (
                  <motion.div
                    key={p.id}
                    initial={{ opacity: 0.8, scale: 0.5, y: 0 }}
                    animate={{ opacity: 0, scale: 1.5, y: -30 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="absolute w-1 h-1 rounded-full bg-orange-400"
                    style={{ left: p.x, bottom: 20 }}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* ── Footer: Word counter + Status ── */}
          <div
            className={`flex items-center justify-between gap-4 px-5 py-3 border-t ${
              focusMode ? "border-white/10" : "border-slate-200/60 dark:border-slate-700/60"
            }`}
          >
            {/* Left: Word counter + Target Ring */}
            <div className="flex items-center gap-4">
              {/* Target Ring */}
              <div className="relative" style={{ width: ringSize, height: ringSize }}>
                <svg width={ringSize} height={ringSize} className="-rotate-90">
                  {/* Background ring */}
                  <circle
                    cx={ringSize / 2}
                    cy={ringSize / 2}
                    r={radius}
                    stroke="currentColor" className={focusMode ? "text-white/10" : "text-black/10 dark:text-white/10"}
                    strokeWidth={strokeWidth}
                    fill="none"
                  />
                  {/* Progress ring */}
                  <motion.circle
                    cx={ringSize / 2}
                    cy={ringSize / 2}
                    r={radius}
                    stroke={ringColor}
                    strokeWidth={strokeWidth}
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    animate={{ strokeDashoffset }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    style={{
                      filter: reachedMin ? `drop-shadow(0 0 6px ${ringColor})` : undefined,
                    }}
                  />
                </svg>
                {/* Center text */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span
                    className={`text-lg font-bold tabular-nums ${
                      focusMode ? "text-white" : "text-slate-900 dark:text-white"
                    }`}
                  >
                    {wordCount}
                  </span>
                  <span
                    className={`text-[9px] uppercase tracking-wider font-semibold ${
                      focusMode ? "text-slate-500 dark:text-slate-400" : "text-slate-400"
                    }`}
                  >
                    {t("write.words")}
                  </span>
                </div>

                {/* Neon glow when target reached */}
                {reachedMin && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: [0.5, 1, 0.5], scale: 1 }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="absolute -inset-1 rounded-full pointer-events-none"
                    style={{
                      background: `radial-gradient(circle, ${ringColor}30, transparent 70%)`,
                    }}
                  />
                )}
              </div>

              {/* Stats */}
              <div className="space-y-0.5">
                <div
                  className={`text-xs font-semibold ${
                    focusMode ? "text-slate-300" : "text-slate-700 dark:text-slate-200"
                  }`}
                >
                  {maxWords
                    ? t("write.target", { a: targetMin, b: maxWords })
                    : t("write.target_min", { a: targetMin })}
                </div>
                <div
                  className={`text-[10px] ${
                    focusMode ? "text-slate-500 dark:text-slate-400" : "text-slate-400"
                  }`}
                >
                  {t("write.chars", { n: charCount })}
                </div>
                <div
                  className={`text-[10px] font-semibold ${
                    exceededMax
                      ? "text-red-500"
                      : reachedMin
                      ? "text-emerald-600"
                      : focusMode
                      ? "text-slate-500 dark:text-slate-400"
                      : "text-slate-500 dark:text-slate-400"
                  }`}
                >
                  {exceededMax
                    ? t("write.over", { n: wordCount - maxWords })
                    : reachedMin
                    ? t("write.reached")
                    : t("write.more", { n: targetMin - wordCount })}
                </div>
              </div>
            </div>

            {/* Right: Save status */}
            <div className="flex items-center gap-2">
              <AnimatePresence mode="wait">
                {isSaving ? (
                  <motion.div
                    key="saving"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400"
                  >
                    <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" />
                    {t("write.saving")}
                  </motion.div>
                ) : (
                  <motion.div
                    key="saved"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex items-center gap-1.5 text-xs text-emerald-600"
                  >
                    <svg
                      className="w-3.5 h-3.5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2.5}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    {t("write.saved")}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}