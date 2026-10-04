"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { getSessionToken } from "@/lib/session";
import { useLanguage } from "@/app/providers";
import AppTopBar from "@/components/AppTopBar";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://myestroeco-backend-production.up.railway.app";

interface Exam {
  id: number;
  code: string;
  title: string;
  description: string | null;
  exam_type: string;
  cefr_level: string | null;
  time_limit_sec: number;
}

const TYPE_INFO: Record<
  string,
  { icon: string; gradient: string }
> = {
  full: {
    icon: "🎯",
    gradient: "from-indigo-500 to-purple-600",
  },
  listening: {
    icon: "🎧",
    gradient: "from-blue-500 to-cyan-500",
  },
  reading: {
    icon: "📖",
    gradient: "from-emerald-500 to-teal-500",
  },
  writing: {
    icon: "✍️",
    gradient: "from-amber-500 to-orange-500",
  },
  speaking: {
    icon: "🎤",
    gradient: "from-rose-500 to-pink-500",
  },
};

const TYPE_TABS = [
  { key: "full", icon: "🎯" },
  { key: "listening", icon: "🎧" },
  { key: "reading", icon: "📖" },
  { key: "writing", icon: "✍️" },
  { key: "speaking", icon: "🎤" },
];

function ExamsContent() {
  const router = useRouter();
  const { t } = useLanguage();
  const searchParams = useSearchParams();
  const type = searchParams.get("type") || "reading";

  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [starting, setStarting] = useState<number | null>(null);

  const typeInfo = TYPE_INFO[type] || TYPE_INFO.reading;

  useEffect(() => {
    loadExams();
  }, [type]);

  async function loadExams() {
    setLoading(true);
    setError("");
    try {
      // ✅ 2. Tokenni o'qib olamiz
      const token = getSessionToken();
      
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      
      // ✅ 3. Agar token bo'lsa, Authorization headeriga qo'shamiz
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const res = await fetch(`${API_URL}/api/v2/exam/exams?type=${type}`, {
        method: "GET",
        headers,
        // credentials: "include" ni qoldirish mumkin, lekin asosiy yuk Authorization headerida
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      setExams(data.items || []);
    } catch (err) {
      console.error("Exam'lar yuklanmadi:", err);
      setError(t("exams.err_load"));
      // Agar 401 bo'lsa, avtomatik login sahifasiga yo'naltirish ham yaxshi amaliyot:
      if (err instanceof Error && err.message.includes("401")) {
        router.push("/login");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleStart(examId: number) {
    setStarting(examId);
    setError("");

    try {
      // ✅ 4. Bu yerda ham xuddi shunday header qo'shamiz
      const token = getSessionToken();
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const res = await fetch(`${API_URL}/api/v2/exam/exams/${examId}/attempts`, {
        method: "POST",
        headers,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      router.push(`/exams/${data.attempt_id}`);
    } catch (err) {
      console.error("Attempt yaratish xatosi:", err);
      setError(err instanceof Error ? err.message : t("exams.err_start"));
      setStarting(null);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-rose-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      {/* ═══ HEADER ═══ */}
      <header className="sticky top-0 z-40 bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl border-b border-slate-100 dark:border-slate-800">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/cabinet" className="flex items-center gap-2 text-slate-700 dark:text-slate-200 hover:text-orange-600 transition-colors">
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            <span className="font-medium">{t("exams.back")}</span>
          </Link>

          <Link href="/" className="flex items-center gap-2">
            <Image
              src="/logo.png"
              alt="Maestro Exam"
              width={36}
              height={36}
              className="rounded-lg"
            />
            <span className="text-lg font-bold bg-gradient-to-r from-orange-600 to-rose-500 bg-clip-text text-transparent">
              Maestro Exam
            </span>
          </Link>

          <AppTopBar />
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* ═══ HERO ═══ */}
        <motion.div
          key={type}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mb-8"
        >
          <div className="flex items-center gap-4 mb-2">
            <div
              className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${typeInfo.gradient} flex items-center justify-center text-3xl shadow-lg`}
            >
              {typeInfo.icon}
            </div>
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">
                {t(`section.${type in TYPE_INFO ? type : "reading"}`)}
              </h1>
              <p className="text-slate-600 dark:text-slate-300">{t(`section.${type in TYPE_INFO ? type : "reading"}.desc2`)}</p>
            </div>
          </div>
        </motion.div>

        {/* ═══ TYPE TABS ═══ */}
        <div className="mb-8 overflow-x-auto scrollbar-hide">
          <div className="flex gap-2 min-w-max pb-2">
            {TYPE_TABS.map((tab) => {
              const isActive = tab.key === type;
              return (
                <Link
                  key={tab.key}
                  href={`/exams?type=${tab.key}`}
                  className={`relative px-5 py-3 rounded-xl font-medium text-sm whitespace-nowrap transition-all ${
                    isActive
                      ? "text-white shadow-lg"
                      : "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 hover:bg-slate-50 border border-slate-200 dark:border-slate-800"
                  }`}
                >
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className={`absolute inset-0 bg-gradient-to-r ${
                        TYPE_INFO[tab.key].gradient
                      } rounded-xl`}
                      transition={{ type: "spring", stiffness: 400, damping: 30 }}
                    />
                  )}
                  <span className="relative z-10 flex items-center gap-2">
                    <span>{tab.icon}</span>
                    <span>{t(`section.${tab.key}`)}</span>
                  </span>
                </Link>
              );
            })}
          </div>
        </div>

        {/* ═══ ERROR ═══ */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 p-4 rounded-xl mb-6 flex items-center gap-3"
            >
              <span className="text-xl">❌</span>
              <span>{error}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ═══ EXAM CARDS ═══ */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 animate-pulse"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded w-3/4 mb-3"></div>
                    <div className="flex gap-2">
                      <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded-full w-16"></div>
                      <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded-full w-20"></div>
                    </div>
                  </div>
                  <div className="w-10 h-10 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
                </div>
                <div className="h-10 bg-slate-200 dark:bg-slate-700 rounded-lg"></div>
              </div>
            ))}
          </div>
        ) : exams.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-12 text-center"
          >
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
              {t("exams.empty_title")}
            </h3>
            <p className="text-slate-500 dark:text-slate-400 mb-6">
              {t("exams.empty_text")}
            </p>
            <Link
              href="/cabinet"
              className="inline-block bg-gradient-to-r from-orange-600 to-rose-500 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-shadow"
            >
              {t("exams.choose_other")}
            </Link>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            <AnimatePresence mode="popLayout">
              {exams.map((exam, idx) => (
                <motion.div
                  key={exam.id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: idx * 0.05 }}
                  className="group bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300"
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2 group-hover:text-orange-600 transition-colors">
                        {exam.title}
                      </h3>
                      <div className="flex flex-wrap items-center gap-2">
                        {exam.cefr_level && (
                          <span className="px-3 py-1 bg-gradient-to-r from-orange-100 to-rose-100 text-orange-700 rounded-full text-xs font-bold">
                            {exam.cefr_level}
                          </span>
                        )}
                        <span className="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 rounded-full text-xs font-medium">
                          ⏱️ {t("exams.minutes", { n: Math.floor(exam.time_limit_sec / 60) })}
                        </span>
                      </div>
                    </div>
                    <div
                      className={`w-12 h-12 rounded-xl bg-gradient-to-br ${typeInfo.gradient} flex items-center justify-center text-xl shadow-md`}
                    >
                      {typeInfo.icon}
                    </div>
                  </div>

                  {/* Description */}
                  {exam.description && (
                    <p className="text-sm text-slate-600 dark:text-slate-300 mb-4 line-clamp-2">
                      {exam.description}
                    </p>
                  )}

                  {/* Start button */}
                  <button
                    onClick={() => handleStart(exam.id)}
                    disabled={starting === exam.id}
                    className={`w-full py-3 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 ${
                      starting === exam.id
                        ? "bg-slate-200 dark:bg-slate-700 text-slate-500 dark:text-slate-400 cursor-not-allowed"
                        : `bg-gradient-to-r ${typeInfo.gradient} text-white hover:shadow-lg hover:scale-[1.02]`
                    }`}
                  >
                    {starting === exam.id ? (
                      <>
                        <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></div>
                        {t("exams.starting")}
                      </>
                    ) : (
                      <>
                        {t("exams.start")}
                      </>
                    )}
                  </button>
                </motion.div>
              ))}
            </AnimatePresence>
          </motion.div>
        )}
      </div>
    </main>
  );
}

function ExamsFallback() {
  const { t } = useLanguage();
  return (
        <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 via-white to-rose-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-orange-200 border-t-orange-600 rounded-full animate-spin mx-auto mb-3"></div>
            <p className="text-slate-500 dark:text-slate-400">{t("common.loading")}</p>
          </div>
        </main>
  );
}

export default function ExamsPage() {
  return (
    <Suspense fallback={<ExamsFallback />}>
      <ExamsContent />
    </Suspense>
  );
}
