"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";
// import { API_URL } from "@/lib/api";
import { apiFetch, clearSessionToken } from "@/lib/session";
import { useLanguage } from "@/app/providers";
import AppTopBar from "@/components/AppTopBar";

interface AttemptHistoryItem {
  attempt_id: number;
  exam_id: number;
  exam_title: string;
  exam_type: string;
  cefr_level: string | null;
  status: string;
  started_at: string | null;
  submitted_at: string | null;
  completed_at: string | null;
  deadline: string | null;
  total_score: number;
  max_score: number;
  percentage: number;
  cefr_estimate: string | null;
}

const TYPE_LABELS: Record<string, string> = {
  full: "🎯 Full Exam",
  listening: "🎧 Listening",
  reading: "📖 Reading",
  writing: "✍️ Writing",
  speaking: "🎤 Speaking",
};

const KNOWN_STATUSES = new Set([
  "created",
  "in_progress",
  "submitted",
  "scoring",
  "completed",
  "needs_review",
  "failed",
]);

function statusClass(status: string) {
  if (status === "completed") return "bg-emerald-100 text-emerald-800 border border-emerald-200";
  if (status === "in_progress") return "bg-blue-100 text-blue-800 border border-blue-200";
  if (status === "scoring") return "bg-amber-100 text-amber-800 border border-amber-200";
  if (status === "failed") return "bg-red-100 text-red-800 border border-red-200 dark:border-red-900";
  return "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-800";
}

function formatDate(value: string | null, locale: string) {
  if (!value) return "—";
  return new Date(value).toLocaleString(locale, {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// 1. Animated Counter with Progress Ring
function ProgressRing({ percentage, size = 65, stroke = 5 }: { percentage: number; size?: number; stroke?: number }) {
  const [count, setCount] = useState(0);
  const radius = (size - stroke) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;

  useEffect(() => {
    let startTime: number;
    let animationFrame: number;
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / 1500, 1);
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      setCount(Math.floor(easeOutQuart * percentage));
      if (progress < 1) animationFrame = requestAnimationFrame(animate);
    };
    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [percentage]);

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90 w-full h-full">
        <circle className="text-slate-200" strokeWidth={stroke} stroke="currentColor" fill="transparent" r={radius} cx={size / 2} cy={size / 2} />
        <motion.circle
          className="text-emerald-500"
          strokeWidth={stroke}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          strokeLinecap="round"
          stroke="currentColor"
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
      </svg>
      <span className="absolute text-sm font-bold text-slate-800 dark:text-slate-100">{count}%</span>
    </div>
  );
}

// 2. Interactive Certificate 3D Tilt
function TiltCard({ children, onCelebrate }: { children: React.ReactNode; onCelebrate?: () => void }) {
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.PointerEvent<HTMLDivElement>) => {
    // Touch'da 3D tilt kerak emas: karta header ustiga chiqib ketadi va "yopishib" qoladi
    if (e.pointerType !== "mouse" || !cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = ((y - centerY) / centerY) * -4;
    const rotateY = ((x - centerX) / centerX) * 4;
    cardRef.current.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
  };

  const handleMouseLeave = () => {
    if (!cardRef.current) return;
    cardRef.current.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)";
  };

  return (
    <motion.div
      ref={cardRef}
      onPointerMove={handleMouseMove}
      onPointerLeave={handleMouseLeave}
      onClick={onCelebrate}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm hover:shadow-2xl transition-all duration-300 cursor-pointer group relative overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
      {children}
    </motion.div>
  );
}

export default function ResultsPage() {
  const router = useRouter();
  const { t, locale } = useLanguage();
  const [items, setItems] = useState<AttemptHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    loadResults();
  }, []);

// results/page.tsx ichida

  async function loadResults() {
    setLoading(true);
    setError("");
    try {
      // ✅ TO'G'RI URL: attempts router'ining /me endpoint'i
      const res = await apiFetch("/api/v2/exam/attempts/me");

      if (res.status === 401) {
        clearSessionToken();
        window.location.href = "/login";
        return;
      }     
      
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      
      const data = await res.json();
      setItems(data.items || []);
    } catch (err) {
      console.error("Natijalar yuklanmadi:", err);
      setError(t("results.err_load"));
    } finally {
      setLoading(false);
    }
  }

  function handleOpenAttempt(item: AttemptHistoryItem) {
    if (item.status === "completed") {
      router.push(`/exams/results/${item.attempt_id}`);
      // 4. Confetti Burst on Target Achievement (80% va undan yuqori ball uchun)
      if (item.percentage >= 80) {
        confetti({
          particleCount: 150,
          spread: 70,
          origin: { y: 0.6 },
          colors: ["#10b981", "#3b82f6", "#f59e0b"],
        });
      }
      return;
    }
    if (["created", "in_progress"].includes(item.status)) {
      router.push(`/exams/${item.attempt_id}`);
      return;
    }
    if (item.status === "scoring" || item.status === "submitted") {
      router.push(`/exams/results/${item.attempt_id}`);
      return;
    }
  }

  const filteredItems = items.filter((item) => {
    if (filter === "all") return true;
    if (filter === "completed") return item.status === "completed";
    if (filter === "in_progress") return item.status === "in_progress" || item.status === "created";
    if (filter === "scoring") return item.status === "scoring" || item.status === "submitted";
    return true;
  });

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4" />
          <p className="text-slate-500 dark:text-slate-400">{t("results.loading")}</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* z-30 + deyarli noshaffof fon: kartalar (transform/3D qatlamlari) header ustiga chiqmasin va orqasidan ko'rinmasin */}
      <header className="border-b border-slate-200 dark:border-slate-800 px-4 sm:px-6 py-4 sticky top-0 z-30 backdrop-blur-md bg-white/95 dark:bg-slate-950/95">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <button onClick={() => router.push("/cabinet")} className="text-slate-600 dark:text-slate-300 hover:text-slate-900 font-medium flex items-center gap-2 transition-colors">
            {t("results.back")}
          </button>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t("results.title")}</h1>
            <AppTopBar />
          </div>
        </div>
      </header>

      {/* relative z-0: kartalarning stacking context'lari shu konteyner ichida qoladi */}
      <div className="relative z-0 max-w-5xl mx-auto p-4 sm:p-6">
        {error && (
          <div className="bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 p-4 rounded-xl mb-6 flex items-center gap-3">
            <span className="text-xl">❌</span> {error}
          </div>
        )}

        {/* 3. Filterable Results Matrix */}
        <div className="flex flex-wrap gap-2 mb-8">
          {[
            { id: "all", label: t("results.filter_all") },
            { id: "completed", label: t("status.completed") },
            { id: "in_progress", label: t("status.in_progress") },
            { id: "scoring", label: t("status.scoring") },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setFilter(f.id)}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-all duration-300 ${
                filter === f.id
                  ? "bg-slate-900 text-white shadow-lg scale-105"
                  : "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-800 hover:bg-slate-100"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

        {filteredItems.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-12 text-center shadow-sm"
          >
            <div className="text-6xl mb-4">📭</div>
            <h2 className="text-xl font-bold mb-2 text-slate-900 dark:text-white">{t("results.empty_title")}</h2>
            <p className="text-slate-500 dark:text-slate-400 mb-6">{t("results.empty_text")}</p>
            <button
              onClick={() => router.push("/cabinet")}
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-3 rounded-xl font-semibold transition-all hover:scale-105 active:scale-95"
            >
              {t("results.choose_exam")}
            </button>
          </motion.div>
        ) : (
          <motion.div layout className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <AnimatePresence>
              {filteredItems.map((item) => (
                <TiltCard 
                  key={item.attempt_id} 
                  onCelebrate={item.percentage >= 80 && item.status === "completed" ? () => {
                    confetti({ particleCount: 120, spread: 60, origin: { y: 0.7 }, colors: ["#10b981", "#f59e0b", "#8b5cf6"] });
                  } : undefined}
                >
                  <div className="flex flex-col gap-4 relative z-10">
                    <div className="flex items-start justify-between">
                      <div className="flex flex-wrap gap-2">
                        <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 font-medium">
                          {TYPE_LABELS[item.exam_type] || item.exam_type}
                        </span>
                        {item.cefr_level && (
                          <span className="text-xs px-2.5 py-1 rounded-full bg-purple-100 text-purple-800 font-bold">
                            {item.cefr_level}
                          </span>
                        )}
                        <span className={`text-xs px-2.5 py-1 rounded-full font-bold ${statusClass(item.status)}`}>
                          {KNOWN_STATUSES.has(item.status) ? t(`status.${item.status}`) : item.status}
                        </span>
                      </div>
                      {item.status === "completed" && item.percentage >= 80 && (
                        <span className="text-2xl animate-bounce" title={t("results.great")}>🏆</span>
                      )}
                    </div>

                    <div>
                      <h2 className="text-lg font-bold text-slate-900 dark:text-white group-hover:text-emerald-700 transition-colors">
                        {item.exam_title}
                      </h2>
                      <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                        {formatDate(item.started_at, locale)}
                      </p>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
                      <div className="flex items-center gap-4">
                        <ProgressRing percentage={item.percentage} size={60} stroke={5} />
                        <div className="text-center">
                          <div className="text-xl font-bold text-slate-900 dark:text-white">
                            {item.total_score}<span className="text-slate-400 text-sm">/{item.max_score}</span>
                          </div>
                          <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">{t("results.total_score")}</div>
                        </div>
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenAttempt(item);
                        }}
                        className="bg-slate-900 hover:bg-emerald-600 text-white px-5 py-2.5 rounded-xl font-semibold text-sm transition-all duration-300 hover:shadow-lg active:scale-95"
                      >
                        {item.status === "completed" ? t("results.details") : item.status === "in_progress" ? t("results.continue") : t("results.open")}
                      </button>
                    </div>
                  </div>
                </TiltCard>
              ))}
            </AnimatePresence>
          </motion.div>
        )}
      </div>
    </main>
  );
}