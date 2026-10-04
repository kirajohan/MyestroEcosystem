"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLanguage, type Lang } from "@/app/providers";

export const LANGS: { code: Lang; label: string; flag: string }[] = [
  { code: "uz", label: "O'zbek", flag: "🇺🇿" },
  { code: "ru", label: "Русский", flag: "🇷🇺" },
  { code: "en", label: "English", flag: "🇬🇧" },
];

export default function LanguageSwitcher() {
  const { lang, setLang } = useLanguage();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const current = LANGS.find((l) => l.code === lang) ?? LANGS[0];

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, [open]);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
      >
        <span>{current.flag}</span>
        <span className="hidden sm:inline">{current.label}</span>
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute right-0 mt-2 w-40 rounded-xl shadow-xl border overflow-hidden z-50 bg-white border-slate-200 dark:bg-slate-900 dark:border-slate-800"
          >
            {LANGS.map((l) => (
              <button
                key={l.code}
                onClick={() => {
                  setLang(l.code);
                  setOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                  l.code === lang
                    ? "bg-orange-50 text-orange-600 dark:bg-orange-500/20 dark:text-orange-400"
                    : "text-slate-700 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-800"
                }`}
              >
                <span>{l.flag}</span>
                <span>{l.label}</span>
                {l.code === lang && <span className="ml-auto">✓</span>}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
