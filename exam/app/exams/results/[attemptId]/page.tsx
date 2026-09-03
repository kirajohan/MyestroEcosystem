"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";
import { API_URL } from "@/lib/api";

interface ResultItem {
  item_id: number;
  item_type: string;
  title: string;
  question_text?: string;
  order: number;
  max_score: number;
  user_selected: number[];
  user_text?: string;
  correct_option_ids: number[];
  auto_score?: number;
  ai_score?: number;
  final_score: number;
  is_correct?: boolean;
  ai_status?: string;
}

interface ResultBlock {
  block_id: number;
  block_type: string;
  title: string;
  score: number;
  status: string;
  items: ResultItem[];
}

interface ResultData {
  attempt_id: number;
  exam_id: number;
  exam_title: string;
  exam_type: string;
  status: string;
  total_score: number;
  percentage: number;
  cefr_estimate: string;
  started_at?: string;
  submitted_at?: string;
  blocks: ResultBlock[];
}

// 1. Animated Counter with Progress Ring
function ProgressRing({ percentage, size = 120, stroke = 8 }: { percentage: number; size?: number; stroke?: number }) {
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
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-bold text-slate-800">{count}%</span>
        <span className="text-xs text-slate-500 font-medium">Natija</span>
      </div>
    </div>
  );
}

// 2. Interactive 3D Tilt Card
function TiltCard({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = ((y - centerY) / centerY) * -3;
    const rotateY = ((x - centerX) / centerX) * 3;
    cardRef.current.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.01, 1.01, 1.01)`;
  };

  const handleMouseLeave = () => {
    if (!cardRef.current) return;
    cardRef.current.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)";
  };

  return (
    <motion.div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 hover:shadow-xl transition-all duration-300 cursor-default group relative overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
      {children}
    </motion.div>
  );
}

export default function ResultPage() {
  const router = useRouter();
  const params = useParams();
  const attemptId = Number(params.attemptId);
  const hasCelebrated = useRef(false);

  const [result, setResult] = useState<ResultData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadResult();
  }, [attemptId]);

  // 3. Confetti Burst on High Achievement
  useEffect(() => {
    if (result && result.percentage >= 70 && !hasCelebrated.current) {
      hasCelebrated.current = true;
      confetti({
        particleCount: 200,
        spread: 80,
        origin: { y: 0.6 },
        colors: ["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6"],
      });
    }
  }, [result]);

  async function loadResult() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/api/v2/exam/attempts/${attemptId}/result`, { credentials: "include" });

      if (!res.ok) {
        if (res.status === 400) {
          throw new Error("Attempt hali yakunlanmagan");
        }
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Natija yuklanmadi:", err);
      setError(err instanceof Error ? err.message : "Natija yuklanmadi");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-slate-500">Natija yuklanmoqda...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-xl shadow p-8 text-center max-w-md"
        >
          <div className="text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Xatolik</h2>
          <p className="text-slate-600 mb-6">{error}</p>
          <button
            onClick={() => router.push("/cabinet")}
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2.5 rounded-lg font-semibold transition-all hover:scale-105 active:scale-95"
          >
            Kabinetga qaytish
          </button>
        </motion.div>
      </main>
    );
  }

  if (!result) return null;

  const totalItems = result.blocks.reduce((sum, b) => sum + b.items.length, 0);
  const correctItems = result.blocks.reduce(
    (sum, b) => sum + b.items.filter((i) => i.is_correct === true).length,
    0
  );

  return (
    <main className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 px-6 py-4 sticky top-0 z-10 backdrop-blur-md bg-white/80">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <button
            onClick={() => router.push("/cabinet")}
            className="text-slate-600 hover:text-slate-900 font-medium flex items-center gap-2 transition-colors"
          >
            ← Kabinetga qaytish
          </button>
          <h1 className="text-xl font-bold text-slate-900">Imtihon Natijasi</h1>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-6 space-y-8">
        
        {/* Umumiy Ball va Statistika */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-white rounded-3xl shadow-sm border border-slate-200 p-8 text-center relative overflow-hidden"
        >
          <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-emerald-400 via-blue-500 to-purple-500" />
          
          <div className="text-6xl mb-4 animate-bounce">
            {result.percentage >= 80 ? "🏆" : result.percentage >= 50 ? "👍" : "💪"}
          </div>
          
          <h2 className="text-3xl font-bold text-slate-900 mb-2">{result.exam_title}</h2>
          <p className="text-slate-500 mb-8 capitalize text-lg">{result.exam_type} imtihoni</p>

          <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-12 mb-8">
            <ProgressRing percentage={result.percentage} size={140} stroke={10} />
            
            <div className="flex flex-col gap-4 text-left">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 text-xl font-bold">
                  {result.total_score}
                </div>
                <div>
                  <div className="text-sm text-slate-500">Jami ball</div>
                  <div className="font-semibold text-slate-900">Maksimal: {result.blocks.reduce((sum, b) => sum + b.items.reduce((isum, i) => isum + i.max_score, 0), 0)}</div>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center text-purple-600 text-xl font-bold">
                  {result.cefr_estimate}
                </div>
                <div>
                  <div className="text-sm text-slate-500">Taxminiy daraja</div>
                  <div className="font-semibold text-slate-900">CEFR Level</div>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-center gap-6 text-sm bg-slate-50 p-4 rounded-xl inline-flex">
            <span className="text-slate-600">
              📝 Jami: <strong className="text-slate-900">{totalItems}</strong>
            </span>
            <span className="w-px h-4 bg-slate-300"></span>
            <span className="text-emerald-600">
              ✅ Togri: <strong>{correctItems}</strong>
            </span>
            <span className="w-px h-4 bg-slate-300"></span>
            <span className="text-red-600">
              ❌ Xato: <strong>{totalItems - correctItems}</strong>
            </span>
          </div>
        </motion.div>

        {/* Blocklar (Listening, Reading va hokazo) */}
        <div className="space-y-6">
          {result.blocks.map((block, index) => (
            <TiltCard key={block.block_id} delay={index * 0.1}>
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
                <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                  {block.block_type === "listening" && "🎧"}
                  {block.block_type === "reading" && "📖"}
                  {block.block_type === "writing" && "✍️"}
                  {block.block_type === "speaking" && "🎤"}
                  {block.title}
                </h3>
                <span className="px-4 py-1.5 bg-emerald-100 text-emerald-800 rounded-full text-sm font-bold border border-emerald-200">
                  Ball: {block.score}
                </span>
              </div>

              <div className="space-y-4">
                <AnimatePresence>
                  {block.items.map((item, itemIndex) => (
                    <motion.div
                      key={item.item_id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: itemIndex * 0.05 }}
                      className={`border rounded-xl p-4 transition-all duration-300 ${
                        item.is_correct === true
                          ? "border-emerald-200 bg-emerald-50/50"
                          : item.is_correct === false
                          ? "border-red-200 bg-red-50/50"
                          : "border-slate-200 bg-slate-50/50"
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        <span className="text-2xl flex-shrink-0 mt-1">
                          {item.is_correct === true ? "✅" : item.is_correct === false ? "❌" : "⚪"}
                        </span>

                        <div className="flex-1">
                          <h4 className="font-semibold text-slate-900 mb-2 text-base">
                            {item.order}. {item.question_text || item.title}
                          </h4>

                          {item.user_selected && item.user_selected.length > 0 && (
                            <p className="text-sm text-slate-600 mb-1">
                              Sizning javobingiz:{" "}
                              <span className={item.is_correct ? "text-emerald-700 font-bold" : "text-red-700 font-bold"}>
                                Variant {item.user_selected.join(", ")}
                              </span>
                            </p>
                          )}

                          {item.user_text && (
                            <div className="bg-white p-3 rounded-lg border border-slate-200 mb-2">
                              <p className="text-sm text-slate-700 italic">"{item.user_text}"</p>
                            </div>
                          )}

                          {item.is_correct === false && item.correct_option_ids.length > 0 && (
                            <p className="text-sm text-emerald-700 mt-2 flex items-center gap-2">
                              <span className="text-lg">💡</span>
                              <span>Togri javob: <span className="font-bold">Variant {item.correct_option_ids.join(", ")}</span></span>
                            </p>
                          )}

                          <div className="flex items-center gap-3 mt-3">
                            <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-slate-200 text-slate-700">
                              Ball: {item.final_score} / {item.max_score}
                            </span>
                            {item.ai_status === "completed" && (
                              <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-purple-100 text-purple-700 flex items-center gap-1">
                                🤖 AI tekshiruvidan o'tgan
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </TiltCard>
          ))}
        </div>

        {/* Harakat Tugmalari */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="flex flex-col sm:flex-row gap-4 pb-12"
        >
          <button
            onClick={() => router.push("/cabinet")}
            className="flex-1 bg-white border border-slate-300 hover:bg-slate-50 text-slate-800 py-3.5 rounded-xl font-semibold transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            🏠 Kabinetga qaytish
          </button>
          <button
            onClick={() => router.push(`/exams?type=${result.exam_type}`)}
            className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-3.5 rounded-xl font-semibold shadow-lg shadow-emerald-200 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            🔄 Yana imtihon topshirish
          </button>
        </motion.div>
      </div>
    </main>
  );
}