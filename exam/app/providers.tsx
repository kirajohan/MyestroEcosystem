"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  ReactNode,
} from "react";
import { translate, LOCALES, type Lang } from "@/lib/i18n";

// localStorage Safari private mode va in-app brauzerlarda xato tashlashi mumkin
function readStorage(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function writeStorage(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* ignore */
  }
}

// ═══════════════════════════════════════════════════════════
// THEME CONTEXT
// ═══════════════════════════════════════════════════════════

type Theme = "light" | "dark";

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const noop = () => {};
const SSR_THEME: ThemeContextType = { theme: "light", toggleTheme: noop };

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light");
  const [mounted, setMounted] = useState(false);

  // Client-side: theme ni localStorage dan o'qish
  useEffect(() => {
    const saved = readStorage("theme") as Theme | null;
    if (saved === "dark" || saved === "light") {
      setTheme(saved);
    } else if (
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
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
    writeStorage("theme", theme);
  }, [theme, mounted]);

  const toggleTheme = useCallback(
    () => setTheme((t) => (t === "light" ? "dark" : "light")),
    []
  );

  const value = useMemo<ThemeContextType>(
    () => (mounted ? { theme, toggleTheme } : SSR_THEME),
    [mounted, theme, toggleTheme]
  );

  // SSR da har doim "light" qaytarish (hydration mismatch bo'lmaydi)
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) return { theme: "light" as Theme, toggleTheme: () => {} };
  return ctx;
}

// ═══════════════════════════════════════════════════════════
// LANGUAGE CONTEXT
// ═══════════════════════════════════════════════════════════

export type { Lang };

interface LanguageContextType {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
  locale: string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>("uz");

  useEffect(() => {
    const saved = readStorage("lang") as Lang | null;
    if (saved === "uz" || saved === "ru" || saved === "en") {
      setLangState(saved);
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    writeStorage("lang", l);
  }, []);

  const value = useMemo<LanguageContextType>(
    () => ({
      lang,
      setLang,
      locale: LOCALES[lang],
      t: (key, vars) => translate(lang, key, vars),
    }),
    [lang, setLang]
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage(): LanguageContextType {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    return {
      lang: "uz",
      setLang: () => {},
      locale: LOCALES.uz,
      t: (key, vars) => translate("uz", key, vars),
    };
  }
  return ctx;
}
