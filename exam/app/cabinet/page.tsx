"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import { getMe, logout } from "@/lib/api";
import { useLanguage } from "@/app/providers";
import AppTopBar from "@/components/AppTopBar";

interface UserInfo {
  id: number;
  full_name: string | null;
  cefr_level: string | null;
  role: string;
  telegram_photo_url?: string | null;
}

const SECTIONS = [
  {
    key: "full",
    icon: "🎯",
    gradient: "from-indigo-500 to-purple-600",
    span: "md:col-span-2",
  },
  {
    key: "listening",
    icon: "🎧",
    gradient: "from-blue-500 to-cyan-500",
    span: "",
  },
  {
    key: "reading",
    icon: "📖",
    gradient: "from-emerald-500 to-teal-500",
    span: "",
  },
  {
    key: "writing",
    icon: "✍️",
    gradient: "from-amber-500 to-orange-500",
    span: "",
  },
  {
    key: "speaking",
    icon: "🎤",
    gradient: "from-rose-500 to-pink-500",
    span: "",
  },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export default function CabinetPage() {
  const { t } = useLanguage();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      const res = await getMe();
      if (res.ok && res.data) {
        setUser(res.data as UserInfo);
        setLoading(false);
      } else {
        await logout();
        window.location.replace("/login");
      }
    }
    loadUser();
  }, []);

  async function handleLogout() {
    await logout();
    window.location.replace("/login");
  }

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 via-white to-rose-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="relative w-16 h-16 mx-auto mb-4">
            <div className="absolute inset-0 rounded-full border-4 border-orange-200"></div>
            <div className="absolute inset-0 rounded-full border-4 border-orange-600 border-t-transparent animate-spin"></div>
          </div>
          <p className="text-slate-600 dark:text-slate-300 font-medium">{t("common.loading")}</p>
        </motion.div>
      </main>
    );
  }

  const displayName = user?.full_name || t("cabinet.user_default");
  const greeting = t(getGreetingKey());

  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-rose-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      {/* ═══ HEADER ═══ */}
      <header className="sticky top-0 z-40 bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl border-b border-slate-100 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <Image
              src="/logo.png"
              alt="Maestro Exam"
              width={40}
              height={40}
              className="rounded-xl"
            />
            <span className="text-xl font-bold bg-gradient-to-r from-orange-600 to-rose-500 bg-clip-text text-transparent">
              Maestro Exam
            </span>
          </Link>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex flex-col items-end">
              <p className="font-semibold text-slate-900 dark:text-white">{displayName}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {t("cabinet.level")}: {user?.cefr_level || "—"}
              </p>
            </div>
            <AppTopBar />
            <button
              onClick={handleLogout}
              className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-orange-600 px-3 py-2 rounded-lg hover:bg-orange-50 dark:hover:bg-slate-800 transition-colors"
            >
              {t("common.logout")}
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8 md:py-12">
        {/* ═══ HERO / GREETING ═══ */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-orange-500 via-orange-600 to-rose-500 p-8 md:p-12 text-white shadow-2xl">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2"></div>

            <div className="relative z-10">
              <p className="text-orange-100 text-sm md:text-base mb-2">
                {greeting}
              </p>
              <h1 className="text-3xl md:text-5xl font-bold mb-3">
                {displayName} 👋
              </h1>
              <p className="text-orange-100 text-base md:text-lg max-w-2xl">
                {t("cabinet.hero_text")}
              </p>

              <div className="flex flex-wrap gap-3 mt-6">
                <div className="bg-white/20 backdrop-blur-sm rounded-xl px-4 py-2 border border-white/30">
                  <div className="text-xs text-orange-100">{t("cabinet.level")}</div>
                  <div className="font-bold">{user?.cefr_level || "—"}</div>
                </div>
                <div className="bg-white/20 backdrop-blur-sm rounded-xl px-4 py-2 border border-white/30">
                  <div className="text-xs text-orange-100">{t("cabinet.role")}</div>
                  <div className="font-bold capitalize">{user?.role || "user"}</div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* ═══ SECTIONS TITLE ═══ */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white">
              {t("cabinet.sections_title")}
            </h2>
            <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
              {t("cabinet.sections_sub")}
            </p>
          </div>
        </div>

        {/* ═══ SECTIONS GRID ═══ */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-10"
        >
          {SECTIONS.map((section) => (
            <motion.div key={section.key} variants={item} className={section.span}>
              <Link
                href={`/exams?type=${section.key}`}
                className="group relative block h-full bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 overflow-hidden"
              >
                {/* Hover gradient background */}
                <div
                  className={`absolute inset-0 bg-gradient-to-br ${section.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}
                ></div>

                <div className="relative z-10">
                  <div
                    className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${section.gradient} flex items-center justify-center text-2xl mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}
                  >
                    {section.icon}
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2 group-hover:text-orange-600 transition-colors">
                    {t(`section.${section.key}`)}
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">{t(`section.${section.key}.desc`)}</p>

                  <div className="mt-4 flex items-center text-sm font-semibold text-orange-600 opacity-0 group-hover:opacity-100 transition-opacity">
                    {t("cabinet.start")}
                    <svg
                      className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M17 8l4 4m0 0l-4 4m4-4H3"
                      />
                    </svg>
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </motion.div>

        {/* ═══ MY RESULTS ═══ */}
        <Link
          href="/exams/results"
          className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6 text-white hover:shadow-2xl transition-all duration-300 block"
        >
          <div className="absolute top-0 right-0 w-40 h-40 bg-orange-500/20 rounded-full blur-3xl"></div>
          <div className="relative z-10">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-rose-500 flex items-center justify-center text-2xl">
                📊
              </div>
              <div>
                <h3 className="text-lg font-bold">{t("cabinet.my_results")}</h3>
                <p className="text-sm text-slate-400">
                  {t("cabinet.my_results_sub")}
                </p>
              </div>
            </div>
            <div className="flex items-center text-sm font-semibold text-orange-400 group-hover:translate-x-1 transition-transform">
              {t("cabinet.view")}
              <svg
                className="w-4 h-4 ml-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 8l4 4m0 0l-4 4m4-4H3"
                />
              </svg>
            </div>
          </div>
        </Link>
      </div>
    </main>
  );
}

function getGreetingKey(): string {
  const hour = new Date().getHours();
  if (hour < 6) return "cabinet.greet_night";
  if (hour < 12) return "cabinet.greet_morning";
  if (hour < 18) return "cabinet.greet_day";
  return "cabinet.greet_evening";
}
