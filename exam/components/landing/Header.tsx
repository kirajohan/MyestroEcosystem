"use client";

import Link from "next/link";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { useTheme, useLanguage } from "@/app/providers";
import LanguageSwitcher from "@/components/LanguageSwitcher";

export default function Header() {
  const { theme, toggleTheme } = useTheme();
  const { t } = useLanguage();
  const isDark = theme === "dark";

  const navLinks = [
    { href: "#features", label: t("nav_features") },
    { href: "#method", label: t("nav_method") },
    { href: "#results", label: t("nav_results") },
    { href: "#faq", label: t("nav_faq") },
  ];

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 1.4, duration: 0.6 }}
      className={`sticky top-0 z-40 backdrop-blur-xl border-b transition-colors ${
        isDark
          ? "bg-slate-950/70 border-slate-800"
          : "bg-white/70 border-slate-200"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3">
          <Image src="/logo.png" alt="Maestro" width={40} height={40} className="rounded-lg" />
          <span className={`text-xl font-bold ${isDark ? "text-white" : "text-slate-900"}`}>
            Maestro Exam
          </span>
        </Link>

        {/* Nav */}
        <nav className="hidden md:flex items-center gap-7">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className={`text-sm font-medium transition-colors ${
                isDark ? "text-slate-300 hover:text-orange-400" : "text-slate-600 hover:text-orange-600"
              }`}
            >
              {link.label}
            </a>
          ))}
        </nav>

        {/* Right: Lang + Theme + Login */}
        <div className="flex items-center gap-2">
          <LanguageSwitcher />

          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className={`p-2 rounded-lg transition-colors ${
              isDark ? "text-slate-300 hover:bg-slate-800" : "text-slate-600 hover:bg-slate-100"
            }`}
            aria-label={t("common.theme_toggle")}
          >
            <AnimatePresence mode="wait">
              {isDark ? (
                <motion.svg
                  key="sun"
                  initial={{ rotate: -90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: 90, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </motion.svg>
              ) : (
                <motion.svg
                  key="moon"
                  initial={{ rotate: 90, opacity: 0 }}
                  animate={{ rotate: 0, opacity: 1 }}
                  exit={{ rotate: -90, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </motion.svg>
              )}
            </AnimatePresence>
          </button>

          {/* Login */}
          <Link
            href="/login"
            className={`text-sm font-semibold px-5 py-2.5 rounded-lg transition-colors ${
              isDark
                ? "bg-orange-500 hover:bg-orange-600 text-white"
                : "bg-orange-600 hover:bg-orange-700 text-white"
            }`}
          >
            {t("nav_login")}
          </Link>
        </div>
      </div>
    </motion.header>
  );
}