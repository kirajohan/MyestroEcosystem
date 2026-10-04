"use client";

import LanguageSwitcher from "@/components/LanguageSwitcher";
import { useLanguage, useTheme } from "@/app/providers";

// Login, cabinet va exam sahifalari uchun: til + tema tugmasi.
export default function AppTopBar({ className = "" }: { className?: string }) {
  const { theme, toggleTheme } = useTheme();
  const { t } = useLanguage();

  return (
    <div className={`flex items-center gap-1 ${className}`}>
      <LanguageSwitcher />
      <button
        onClick={toggleTheme}
        aria-label={t("common.theme_toggle")}
        className="p-2 rounded-lg transition-colors text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
      >
        {theme === "dark" ? "☀️" : "🌙"}
      </button>
    </div>
  );
}
