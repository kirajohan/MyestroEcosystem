"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLanguage } from "@/app/providers";

interface ReadingPassageProps {
  text: string;
  title?: string;
  instruction?: string;  // ← YANGI

}

const HIGHLIGHT_COLORS = [
  { name: "Yellow", value: "rgba(253, 224, 71, 0.55)" },
  { name: "Green", value: "rgba(134, 239, 172, 0.55)" },
  { name: "Purple", value: "rgba(216, 180, 254, 0.55)" },
];

export default function ReadingPassage({ 
  text, 
  title,
  instruction  // ← YANGI
}: ReadingPassageProps) {
  const { t } = useLanguage();

  const scrollRef = useRef<HTMLDivElement>(null);
  const toolbarRef = useRef<HTMLDivElement>(null);
  const dictRef = useRef<HTMLDivElement>(null);

  const [progress, setProgress] = useState(0);
  const [fontSize, setFontSize] = useState(16);
  const [serif, setSerif] = useState(false);
  const [focusMode, setFocusMode] = useState(false);
  const [collapsed, setCollapsed] = useState<Record<number, boolean>>({});

  const [toolbar, setToolbar] = useState<{ x: number; y: number; text: string } | null>(null);
  const [dict, setDict] = useState<{
    x: number;
    y: number;
    word: string;
    data: any;
    loading: boolean;
  } | null>(null);

  const paragraphs = text.split(/\n\n+/).map((p) => p.trim()).filter(Boolean);
  const wordCount = text.split(/\s+/).filter(Boolean).length;
  const readTime = Math.max(1, Math.round(wordCount / 200));

  // ── Scroll progress ────────────────────────────────────
  const handleScroll = () => {
    const el = scrollRef.current;
    if (!el) return;
    const max = el.scrollHeight - el.clientHeight;
    setProgress(max > 0 ? Math.min(1, el.scrollTop / max) : 0);
    setToolbar(null);
    setDict(null);
  };

  // ── Selection → toolbar ────────────────────────────────
  const handleMouseUp = () => {
    window.setTimeout(() => {
      const sel = window.getSelection();
      if (!sel || sel.isCollapsed || !sel.toString().trim()) {
        setToolbar(null);
        return;
      }
      const selectedText = sel.toString().replace(/\s+/g, " ").trim();
      if (!selectedText || selectedText.length > 80) {
        setToolbar(null);
        return;
      }
      const rect = sel.getRangeAt(0).getBoundingClientRect();
      const x = Math.max(8, Math.min(rect.left + rect.width / 2 - 90, window.innerWidth - 200));
      const y = Math.max(8, rect.top - 52);
      setToolbar({ x, y, text: selectedText });
    }, 10);
  };

  // ── Outside click → close dict ─────────────────────────
  useEffect(() => {
    const onDown = (e: MouseEvent) => {
      if (toolbarRef.current?.contains(e.target as Node)) return;
      if (dictRef.current?.contains(e.target as Node)) return;
      setDict(null);
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, []);

  // ── Highlight selection ────────────────────────────────
  const applyHighlight = (color: string) => {
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) return;
    const range = sel.getRangeAt(0);
    const span = document.createElement("span");
    span.style.backgroundColor = color;
    span.style.borderRadius = "4px";
    span.style.padding = "0 2px";
    (span.style as any).boxDecorationBreak = "clone";
    try {
      range.surroundContents(span);
    } catch {
      // Murakkab selection — o'tkazib yuboramiz
    }
    setToolbar(null);
    sel.removeAllRanges();
  };

  // ── Dictionary (free API) ──────────────────────────────
  const openDictionary = async (rawWord: string, x: number, y: number) => {
    const word = rawWord.split(" ")[0].replace(/[^a-zA-Z'-]/g, "");
    if (!word) return;
    setDict({ x, y, word, data: null, loading: true });
    try {
      const res = await fetch(
        `https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(word.toLowerCase())}`
      );
      if (!res.ok) throw new Error();
      const json = await res.json();
      setDict({ x, y, word, data: json[0], loading: false });
    } catch {
      setDict({ x, y, word, data: null, loading: false });
    }
  };

  // ── Pronunciation (browser TTS) ────────────────────────
  const speak = (t: string) => {
    try {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(t);
      u.lang = "en-US";
      u.rate = 0.95;
      window.speechSynthesis.speak(u);
    } catch {}
  };

  const fontFamily = serif ? "Georgia, 'Times New Roman', serif" : undefined;

  // ═══════════════════════════════════════════════════════
  // FOCUS MODE: Faqat chap ustunni kengaytiradi,
  // o'ng ustun (savollar) ko'rinib turadi
  // ═══════════════════════════════════════════════════════

  return (
    <>
      {/* ═══ MAIN CONTAINER ═══ */}
      <div
        className={`relative overflow-hidden rounded-2xl border shadow-xl transition-all duration-500 ease-[cubic-bezier(0.22,1,0.36,1)] ${
          focusMode
            ? "bg-slate-900/95 border-white/10 backdrop-blur-xl lg:-mx-4 lg:scale-[1.02]"
            : "bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-slate-200/60 dark:border-slate-700/60"
        }`}
      >
        {/* ── Header: title + controls ── */}
        <div
          className={`flex items-center justify-between gap-3 px-5 py-3 border-b ${
            focusMode ? "border-white/10" : "border-slate-200/60 dark:border-slate-700/60"
          }`}
        >
          <div>
            <h3
              className={`text-xs font-bold uppercase tracking-widest flex items-center gap-2 ${
                focusMode ? "text-orange-400" : "text-orange-600 dark:text-orange-400"
              }`}
            >
              📖 {title || t("read.title_default")}
            </h3>
            <div className={`text-[11px] mt-0.5 ${focusMode ? "text-slate-500" : "text-slate-400"}`}>
              {t("read.stats", { m: readTime, w: wordCount, p: Math.round(progress * 100) })}
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setFontSize((s) => Math.max(13, s - 1))}
              className={`px-2 py-1 rounded-lg text-xs font-bold transition-colors ${
                focusMode ? "text-slate-300 hover:bg-white/10" : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
              }`}
              title={t("read.font_smaller")}
            >
              A−
            </button>
            <button
              onClick={() => setFontSize((s) => Math.min(22, s + 1))}
              className={`px-2 py-1 rounded-lg text-sm font-bold transition-colors ${
                focusMode ? "text-slate-300 hover:bg-white/10" : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
              }`}
              title={t("read.font_larger")}
            >
              A+
            </button>
            <button
              onClick={() => setSerif((v) => !v)}
              className={`px-2 py-1 rounded-lg text-xs font-semibold transition-colors ${
                serif
                  ? "bg-orange-500 text-white"
                  : focusMode
                  ? "text-slate-300 hover:bg-white/10"
                  : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
              }`}
              title={t("read.serif_title")}
              style={{ fontFamily: "Georgia, serif" }}
            >
              Serif
            </button>
            <button
              onClick={() => setFocusMode((v) => !v)}
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors ${
                focusMode
                  ? "bg-orange-500 text-white"
                  : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
              }`}
              title={t("read.focus_title")}
            >
              {focusMode ? t("read.exit") : t("read.focus")}
            </button>
          </div>
        </div>

        {/* ── Instructions (passage tepasida) ── */}
        {instruction && (
          <div
            className={`px-5 py-3 border-b text-sm ${
              focusMode
                ? "bg-blue-950/40 border-white/10 text-blue-300"
                : "bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/50 dark:to-indigo-950/50 border-slate-200/60 dark:border-slate-700/60 text-blue-900 dark:text-blue-200"
            }`}
          >
            <div
              className={`text-[10px] font-bold uppercase tracking-widest mb-1 ${
                focusMode ? "text-blue-400" : "text-blue-700 dark:text-blue-400"
              }`}
            >
              {t("read.instructions")}
            </div>
            <p className="leading-relaxed">{instruction}</p>
          </div>
        )}

        {/* ── Reading progress bar ── */}
        <div className={`h-1 ${focusMode ? "bg-white/10" : "bg-slate-200/60 dark:bg-slate-700/60"}`}>
          <div
            className="h-full bg-gradient-to-r from-orange-500 to-rose-500 transition-[width] duration-150"
            style={{ width: `${progress * 100}%` }}
          />
        </div>

        {/* ── Scrollable text ── */}
        <div
          ref={scrollRef}
          onScroll={handleScroll}
          onMouseUp={handleMouseUp}
          className={`reading-scroll overflow-y-auto px-6 md:px-8 py-6 transition-all duration-500 ${
            focusMode
              ? "max-h-[calc(100vh-140px)]"
              : "max-h-[calc(100vh-220px)]"
          }`}
        >
          {paragraphs.map((p, i) => {
            const isCollapsed = collapsed[i];
            return (
              <div key={i} className="group/para relative">
                {paragraphs.length > 1 && (
                  <button
                    onClick={() => setCollapsed((c) => ({ ...c, [i]: !c[i] }))}
                    className={`absolute -left-5 top-1.5 opacity-0 group-hover/para:opacity-100 transition-opacity text-xs ${
                      focusMode ? "text-slate-500" : "text-slate-400"
                    }`}
                    title={isCollapsed ? t("read.expand") : t("read.collapse")}
                  >
                    {isCollapsed ? "▸" : "▾"}
                  </button>
                )}

                <AnimatePresence initial={false}>
                  {!isCollapsed ? (
                    <motion.p
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                      className={`overflow-hidden leading-relaxed whitespace-pre-line mb-5 ${
                        focusMode ? "text-slate-200" : "text-slate-800 dark:text-slate-200"
                      }`}
                      style={{ fontSize, fontFamily }}
                    >
                      {p}
                    </motion.p>
                  ) : (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className={`text-xs italic mb-5 ${focusMode ? "text-slate-600" : "text-slate-400"}`}
                    >
                      {t("read.collapsed", { n: i + 1 })}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })}
        </div>
      </div>

      {/* ═══ SELECTION TOOLBAR ═══ */}
      <AnimatePresence>
        {toolbar && (
          <motion.div
            ref={toolbarRef}
            initial={{ opacity: 0, y: 6, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="fixed z-[70] flex items-center gap-1.5 px-2 py-1.5 rounded-xl bg-slate-900/95 border border-white/10 shadow-2xl backdrop-blur-xl"
            style={{ left: toolbar.x, top: toolbar.y }}
          >
            {HIGHLIGHT_COLORS.map((c) => (
              <button
                key={c.name}
                onClick={() => applyHighlight(c.value)}
                className="w-6 h-6 rounded-full border-2 border-white/20 hover:scale-110 transition-transform"
                style={{ backgroundColor: c.value }}
                title={t("read.marker", { c: t(`read.color.${c.name}`) })}
              />
            ))}
            <div className="w-px h-5 bg-white/10 mx-0.5" />
            <button
              onClick={() => openDictionary(toolbar.text, toolbar.x, toolbar.y + 52)}
              className="text-sm px-1.5 hover:scale-110 transition-transform"
              title={t("read.dictionary")}
            >
              📖
            </button>
            <button
              onClick={() => speak(toolbar.text)}
              className="text-sm px-1.5 hover:scale-110 transition-transform"
              title={t("read.pronounce")}
            >
              🔊
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ═══ DICTIONARY TOOLTIP ═══ */}
      <AnimatePresence>
        {dict && (
          <motion.div
            ref={dictRef}
            initial={{ opacity: 0, y: 8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed z-[70] w-72 rounded-2xl bg-slate-900/95 border border-white/10 shadow-2xl backdrop-blur-xl p-4 text-white"
            style={{
              left: Math.max(8, Math.min(dict.x, (typeof window !== "undefined" ? window.innerWidth : 400) - 300)),
              top: dict.y,
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg">{dict.word}</span>
                {dict.data?.phonetic && (
                  <span className="text-slate-400 text-sm">{dict.data.phonetic}</span>
                )}
              </div>
              <button
                onClick={() => speak(dict.word)}
                className="w-8 h-8 rounded-full bg-orange-500/20 text-orange-400 hover:bg-orange-500/30 flex items-center justify-center"
              >
                🔊
              </button>
            </div>

            {dict.loading ? (
              <div className="text-sm text-slate-400 animate-pulse">{t("common.loading")}</div>
            ) : dict.data?.meanings?.length ? (
              <div className="space-y-2 max-h-40 overflow-y-auto reading-scroll">
                {dict.data.meanings.slice(0, 2).map((m: any, i: number) => (
                  <div key={i}>
                    <div className="text-[10px] uppercase tracking-widest text-orange-400 font-bold">
                      {m.partOfSpeech}
                    </div>
                    <p className="text-sm text-slate-300">{m.definitions?.[0]?.definition}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-400">{t("read.not_found")}</p>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}