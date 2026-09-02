"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";

// ═══════════════════════════════════════════════════════════
// THEME CONTEXT
// ═══════════════════════════════════════════════════════════

type Theme = "light" | "dark";

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light");
  const [mounted, setMounted] = useState(false);

  // Client-side: theme ni localStorage dan o'qish
  useEffect(() => {
    const saved = localStorage.getItem("theme") as Theme | null;
    if (saved === "dark" || saved === "light") {
      setTheme(saved);
    } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      setTheme("dark");
    }
    setMounted(true);
  }, []);

  // Theme o'zgarganda HTML class ga qo'shish
  useEffect(() => {
    if (!mounted) return;
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem("theme", theme);
  }, [theme, mounted]);

  const toggleTheme = () => setTheme((t) => (t === "light" ? "dark" : "light"));

  // SSR da har doim "light" qaytarish (hydration mismatch bo'lmaydi)
  if (!mounted) {
    return (
      <ThemeContext.Provider value={{ theme: "light", toggleTheme: () => {} }}>
        {children}
      </ThemeContext.Provider>
    );
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) return { theme: "light" as Theme, toggleTheme: () => {} };
  return ctx;
}

// ═══════════════════════════════════════════════════════════
// LANGUAGE CONTEXT
// ═══════════════════════════════════════════════════════════

export type Lang = "uz" | "ru" | "en";

interface LanguageContextType {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const translations: Record<Lang, Record<string, string>> = {
  uz: {
    hero_badge: "Ingliz tili darajangizni aniqlang",
    hero_title_1: "Ingliz tilini",
    hero_title_2: "mukammal o'rganing",
    hero_subtitle: "Listening, Reading, Writing va Speaking bo'yicha real imtihonlar. AI baholash bilan natijangizni darhol oling.",
    cta_start: "Bepul boshlash",
    cta_learn: "Batafsil ma'lumot",
    nav_features: "Imkoniyatlar",
    nav_method: "Metodika",
    nav_results: "Natijalar",
    nav_faq: "FAQ",
    nav_login: "Kirish",
  },
  ru: {
    hero_badge: "Определите свой уровень английского",
    hero_title_1: "Изучайте английский",
    hero_title_2: "совершенно",
    hero_subtitle: "Реальные экзамены по Listening, Reading, Writing и Speaking. Получите результат мгновенно с AI-оценкой.",
    cta_start: "Начать бесплатно",
    cta_learn: "Подробнее",
    nav_features: "Возможности",
    nav_method: "Методика",
    nav_results: "Результаты",
    nav_faq: "FAQ",
    nav_login: "Войти",
  },
  en: {
    hero_badge: "Check your English level",
    hero_title_1: "Master English",
    hero_title_2: "perfectly",
    hero_subtitle: "Real exams in Listening, Reading, Writing and Speaking. Get your result instantly with AI evaluation.",
    cta_start: "Start Free",
    cta_learn: "Learn more",
    nav_features: "Features",
    nav_method: "Method",
    nav_results: "Results",
    nav_faq: "FAQ",
    nav_login: "Login",
  },
};

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>("uz");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("lang") as Lang | null;
    if (saved === "uz" || saved === "ru" || saved === "en") {
      setLangState(saved);
    }
    setMounted(true);
  }, []);

  const setLang = (l: Lang) => {
    setLangState(l);
    localStorage.setItem("lang", l);
  };

  const t = (key: string) => translations[lang][key] || key;

  if (!mounted) {
    return (
      <LanguageContext.Provider value={{ lang: "uz", setLang: () => {}, t: (k) => k }}>
        {children}
      </LanguageContext.Provider>
    );
  }

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) return { lang: "uz" as Lang, setLang: () => {}, t: (key: string) => key };
  return ctx;
}