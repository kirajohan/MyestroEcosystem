"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";
import { API_URL } from "@/lib/api";

// ─── Interfaces (Backend rejasiga to'liq mos) ───────────────────────────────
interface AiFeedback {
  overall_score?: number;
  cefr_estimate?: string;
  criteria?: { name: string; score: number; max_score: number; comment: string }[];
  corrections?: { original: string; corrected: string; explanation: string }[];
  strengths?: string[];
  weaknesses?: string[];
  recommendations?: string[];
}

interface ResultItem {
  item_id: number;
  item_type: string;
  title: string;
  question_text?: string;
  order: number;
  max_score: number;
  user_selected?: number[];
  user_text?: string;
  audio_url?: string;
  transcript_text?: string;
  correct_option_ids?: number[];
  auto_score?: number;
  ai_score?: number;
  final_score: number;
  is_correct?: boolean;
  ai_status?: "pending" | "processing" | "completed" | "error" | "needs_review";
  ai_feedback?: AiFeedback;
}

interface ResultBlock {
  block_id: number;
  block_type: "listening" | "reading" | "writing" | "speaking";
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

// ─── Helper Functions ────────────────────────────────────────────────────────
const isAutoGraded = (type: string) => type === "listening" || type === "reading";
const isAiGraded = (type: string) => type === "writing" || type === "speaking";

// ─── Components ──────────────────────────────────────────────────────────────

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
          className="text-orange-500"
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

function TiltCard({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const cardRef = useRef<HTMLDivElement>(null);
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    cardRef.current.style.transform = `perspective(1000px) rotateX(${((y - centerY) / centerY) * -3}deg) rotateY(${((x - centerX) / centerX) * 3}deg) scale3d(1.01, 1.01, 1.01)`;
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
      <div className="absolute inset-0 bg-gradient-to-br from-orange-500/5 to-rose-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
      {children}
    </motion.div>
  );
}

function AiFeedbackView({ feedback }: { feedback: AiFeedback }) {
  return (
    <div className="mt-4 space-y-4">
      {feedback.criteria && (
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
          <h5 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">📊 Baholash mezonlari</h5>
          <div className="space-y-3">
            {feedback.criteria.map((c, idx) => (
              <div key={idx}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium text-slate-700">{c.name}</span>
                  <span className="text-slate-500">{c.score}/{c.max_score}</span>
                </div>
                <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(c.score / c.max_score) * 100}%` }}
                    transition={{ duration: 1, delay: idx * 0.1 }}
                    className="h-full bg-gradient-to-r from-orange-500 to-rose-500 rounded-full"
                  />
                </div>
                {c.comment && <p className="text-xs text-slate-500 mt-1 italic">"{c.comment}"</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {feedback.corrections && feedback.corrections.length > 0 && (
        <div className="bg-red-50 rounded-xl p-4 border border-red-100">
          <h5 className="text-sm font-bold text-red-800 mb-3 flex items-center gap-2">✏️ Xatolar va tuzatishlar</h5>
          <div className="space-y-3">
            {feedback.corrections.map((corr, idx) => (
              <div key={idx} className="text-sm">
                <p className="text-red-600 line-through mb-1">{corr.original}</p>
                <p className="text-emerald-600 font-semibold mb-1">➔ {corr.corrected}</p>
                <p className="text-slate-600 text-xs bg-white p-2 rounded border border-red-100">💡 {corr.explanation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {feedback.strengths && feedback.strengths.length > 0 && (
          <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-100">
            <h5 className="text-sm font-bold text-emerald-800 mb-2">✅ Kuchli tomonlari</h5>
            <ul className="space-y-1">
              {feedback.strengths.map((s, idx) => (
                <li key={idx} className="text-xs text-emerald-700 flex items-start gap-2"><span className="mt-1">•</span> {s}</li>
              ))}
            </ul>
          </div>
        )}
        {feedback.weaknesses && feedback.weaknesses.length > 0 && (
          <div className="bg-amber-50 rounded-xl p-4 border border-amber-100">
            <h5 className="text-sm font-bold text-amber-800 mb-2">⚠️ Rivojlantirish kerak</h5>
            <ul className="space-y-1">
              {feedback.weaknesses.map((w, idx) => (
                <li key={idx} className="text-xs text-amber-700 flex items-start gap-2"><span className="mt-1">•</span> {w}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {feedback.recommendations && feedback.recommendations.length > 0 && (
        <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
          <h5 className="text-sm font-bold text-blue-800 mb-2">🚀 Tavsiyalar</h5>
          <ul className="space-y-1">
            {feedback.recommendations.map((r, idx) => (
              <li key={idx} className="text-xs text-blue-700 flex items-start gap-2"><span className="mt-1">💡</span> {r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────
export default function ResultPage() {
  const router = useRouter();
  const params = useParams();
  const attemptId = Number(params.attemptId);
  const hasCelebrated = useRef(false);

  const [result, setResult] = useState<ResultData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // ✅ Polling uchun ref ishlatamiz (infinite loop oldini olish uchun)
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const isPollingRef = useRef(false);

  // Dastlabki yuklash
  useEffect(() => {
    loadResult();
    return () => {
      // Cleanup polling on unmount
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, [attemptId]);

  // ✅ Polling mexanizmi - alohida useEffect
  useEffect(() => {
    // Agar result mavjud bo'lmasa yoki status "scoring" bo'lmasa, polling kerak emas
    if (!result || result.status !== "scoring") {
      if (pollingRef.current) {
        console.log("✅ Polling to'xtatildi");
        clearInterval(pollingRef.current);
        pollingRef.current = null;
        isPollingRef.current = false;
      }
      return;
    }

    // Agar allaqachon polling bo'layotgan bo'lsa, qayta boshlamaymiz
    if (isPollingRef.current) {
      return;
    }

    console.log("🔄 AI baholamoqda, polling boshlandi...");
    isPollingRef.current = true;

    pollingRef.current = setInterval(async () => {
      console.log("🔍 Status tekshirilmoqda...");
      try {
        const res = await fetch(`${API_URL}/api/v2/exam/attempts/${attemptId}/result`, {
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          
          // Faqat status yoki natija o'zgargan bo'lsa yangilaymiz
          if (data.status !== result?.status || data.total_score !== result?.total_score) {
            console.log("📊 Natija yangilandi:", data.status);
            setResult(data);
          }
          
          if (data.status === "completed") {
            console.log("✅ AI baholash tugadi!");
            if (pollingRef.current) {
              clearInterval(pollingRef.current);
              pollingRef.current = null;
              isPollingRef.current = false;
            }
          }
        }
      } catch (err) {
        console.error("Polling xatosi:", err);
      }
    }, 3000); // Har 3 sekundda

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
        isPollingRef.current = false;
      }
    };
  }, [result?.status, attemptId]);

  // Confetti animation
  useEffect(() => {
    if (result && result.status === "completed" && result.percentage >= 70 && !hasCelebrated.current) {
      hasCelebrated.current = true;
      confetti({ particleCount: 200, spread: 80, origin: { y: 0.6 }, colors: ["#f97316", "#e11d48", "#3b82f6", "#10b981"] });
    }
  }, [result]);

  // ✅ Yuklash funksiyasi - polling uchun optimallashtirilgan
  async function loadResult(isPolling = false) {
    // Polling paytida loading state'ni o'zgartirmaymiz
    if (!isPolling) {
      setLoading(true);
    }
    setError("");
    
    try {
      const res = await fetch(`${API_URL}/api/v2/exam/attempts/${attemptId}/result`, { 
        credentials: "include" 
      });
      
      if (!res.ok) {
        if (res.status === 400) throw new Error("Attempt hali yakunlanmagan yoki topilmadi");
        throw new Error(`HTTP ${res.status}`);
      }
      
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Natija yuklanmadi:", err);
      // Polling paytida error ko'rsatmaymiz
      if (!isPolling) {
        setError(err instanceof Error ? err.message : "Natija yuklanmadi");
      }
    } finally {
      if (!isPolling) {
        setLoading(false);
      }
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 h-12 border-b-2 border-orange-600 mx-auto mb-4" />
          <p className="text-slate-500">Natija yuklanmoqda...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="bg-white rounded-xl shadow p-8 text-center max-w-md">
          <div className="text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Xatolik</h2>
          <p className="text-slate-600 mb-6">{error}</p>
          <button onClick={() => router.push("/cabinet")} className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-2.5 rounded-lg font-semibold transition-all hover:scale-105 active:scale-95">
            Kabinetga qaytish
          </button>
        </motion.div>
      </main>
    );
  }

  if (!result) return null;

  const autoGradedItems = result.blocks.flatMap((b) => (isAutoGraded(b.block_type) ? b.items : []));
  const correctAutoItems = autoGradedItems.filter((i) => i.is_correct).length;
  const totalAutoItems = autoGradedItems.length;
  const pendingAiBlocks = result.blocks.filter((b) => isAiGraded(b.block_type) && b.items.some((i) => i.ai_status !== "completed")).length;

  return (
    <main className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 px-6 py-4 sticky top-0 z-10 backdrop-blur-md bg-white/80">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <button onClick={() => router.push("/cabinet")} className="text-slate-600 hover:text-slate-900 font-medium flex items-center gap-2 transition-colors">
            ← Kabinetga qaytish
          </button>
          <h1 className="text-xl font-bold text-slate-900">Imtihon Natijasi</h1>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-6 space-y-8">
        
        {/* Global AI Scoring Banner */}
        {result.status === "scoring" && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="bg-amber-50 border border-amber-200 text-amber-800 p-4 rounded-xl flex items-center gap-3">
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }} className="w-5 h-5 border-2 border-amber-600 border-t-transparent rounded-full flex-shrink-0" />
            <div>
              <p className="font-semibold">Natijalar to'liq tayyor emas</p>
              <p className="text-sm text-amber-700">Writing va Speaking qismlari hali AI tomonidan baholanmoqda. Sahifani birozdan keyin yangilab ko'ring.</p>
            </div>
          </motion.div>
        )}

        {/* Umumiy Ball va Statistika */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="bg-white rounded-3xl shadow-sm border border-slate-200 p-8 text-center relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-orange-400 via-rose-500 to-purple-500" />
          
          <div className="text-6xl mb-4 animate-bounce">
            {result.percentage >= 80 ? "🏆" : result.percentage >= 50 ? "👍" : "💪"}
          </div>
          
          <h2 className="text-3xl font-bold text-slate-900 mb-2">{result.exam_title}</h2>
          <p className="text-slate-500 mb-8 capitalize text-lg">{result.exam_type} imtihoni</p>

          <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-12 mb-8">
            <ProgressRing percentage={result.percentage} size={140} stroke={10} />
            
            <div className="flex flex-col gap-4 text-left">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 text-xl font-bold">
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

          {/* Dinamik statistika (Faqat Auto-graded uchun To'g'ri/Xato ko'rsatamiz) */}
          {totalAutoItems > 0 && (
            <div className="flex items-center justify-center gap-6 text-sm bg-slate-50 p-4 rounded-xl inline-flex">
              <span className="text-slate-600">📝 Test savollari: <strong className="text-slate-900">{totalAutoItems}</strong></span>
              <span className="w-px h-4 bg-slate-300"></span>
              <span className="text-emerald-600">✅ To'g'ri: <strong>{correctAutoItems}</strong></span>
              <span className="w-px h-4 bg-slate-300"></span>
              <span className="text-red-600">❌ Xato: <strong>{totalAutoItems - correctAutoItems}</strong></span>
              {pendingAiBlocks > 0 && (
                <>
                  <span className="w-px h-4 bg-slate-300"></span>
                  <span className="text-amber-600">⏳ AI baholamoqda: <strong>{pendingAiBlocks} bo'lim</strong></span>
                </>
              )}
            </div>
          )}
        </motion.div>

        {/* Blocklar */}
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
                <span className={`px-4 py-1.5 rounded-full text-sm font-bold border ${
                  block.status === "completed" ? "bg-emerald-100 text-emerald-800 border-emerald-200" : "bg-amber-100 text-amber-800 border-amber-200"
                }`}>
                  Ball: {block.score}
                </span>
              </div>

              <div className="space-y-4">
                <AnimatePresence>
                  {block.items.map((item, itemIndex) => {
                    // 1. AUTO-GRADED (Listening / Reading)
                    if (isAutoGraded(block.block_type)) {
                      return (
                        <motion.div
                          key={item.item_id}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: itemIndex * 0.05 }}
                          className={`border rounded-xl p-4 transition-all duration-300 ${
                            item.is_correct ? "border-emerald-200 bg-emerald-50/50" : "border-red-200 bg-red-50/50"
                          }`}
                        >
                          <div className="flex items-start gap-4">
                            <span className="text-2xl flex-shrink-0 mt-1">{item.is_correct ? "✅" : "❌"}</span>
                            <div className="flex-1">
                              <h4 className="font-semibold text-slate-900 mb-2 text-base">{item.order}. {item.question_text || item.title}</h4>
                              {item.user_selected && item.user_selected.length > 0 && (
                                <p className="text-sm text-slate-600 mb-1">
                                  Sizning javobingiz: <span className={item.is_correct ? "text-emerald-700 font-bold" : "text-red-700 font-bold"}>Variant {item.user_selected.join(", ")}</span>
                                </p>
                              )}
                              {!item.is_correct && item.correct_option_ids && item.correct_option_ids.length > 0 && (
                                <p className="text-sm text-emerald-700 mt-2 flex items-center gap-2">
                                  <span className="text-lg">💡</span>
                                  <span>To'g'ri javob: <span className="font-bold">Variant {item.correct_option_ids.join(", ")}</span></span>
                                </p>
                              )}
                              <div className="flex items-center gap-3 mt-3">
                                <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-slate-200 text-slate-700">
                                  Ball: {item.final_score} / {item.max_score}
                                </span>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      );
                    }

                    // 2. AI-GRADED (Writing / Speaking) - Pending State
                    if (isAiGraded(block.block_type) && item.ai_status !== "completed") {
                      return (
                        <motion.div
                          key={item.item_id}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="border border-amber-200 bg-amber-50/50 rounded-xl p-6 text-center"
                        >
                          <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }} className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full mx-auto mb-3" />
                          <p className="text-amber-800 font-semibold">AI tomonidan baholanmoqda...</p>
                          <p className="text-amber-600 text-sm mt-1">Bu qismning natijasi birozdan keyin chiqadi.</p>
                        </motion.div>
                      );
                    }

                    // 3. AI-GRADED (Writing / Speaking) - Completed State
                    return (
                      <motion.div
                        key={item.item_id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: itemIndex * 0.05 }}
                        className="border border-slate-200 bg-white rounded-xl p-5 shadow-sm"
                      >
                        {/* User Input Display */}
                        {block.block_type === "writing" && item.user_text && (
                          <div className="mb-4">
                            <h5 className="text-xs font-bold text-slate-500 uppercase mb-2">Sizning javobingiz</h5>
                            <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 text-slate-800 text-sm leading-relaxed whitespace-pre-wrap">
                              {item.user_text}
                            </div>
                          </div>
                        )}
                        
                        {block.block_type === "speaking" && (
                          <div className="mb-4">
                            <h5 className="text-xs font-bold text-slate-500 uppercase mb-2">Sizning javobingiz</h5>
                            {item.audio_url && <audio controls src={item.audio_url} className="w-full mb-3 h-10" />}
                            {item.transcript_text ? (
                              <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 text-slate-800 text-sm leading-relaxed italic">
                                "{item.transcript_text}"
                              </div>
                            ) : (
                              <p className="text-sm text-slate-500 italic">Transkript mavjud emas</p>
                            )}
                          </div>
                        )}

                        {/* AI Feedback Display */}
                        {item.ai_feedback && <AiFeedbackView feedback={item.ai_feedback} />}
                        
                        <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
                          <span className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                            🤖 AI Yakuniy ball
                          </span>
                          <span className="text-lg font-bold text-orange-600">{item.final_score} / {item.max_score}</span>
                        </div>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
              </div>
            </TiltCard>
          ))}
        </div>

        {/* Harakat Tugmalari */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="flex flex-col sm:flex-row gap-4 pb-12">
          <button onClick={() => router.push("/cabinet")} className="flex-1 bg-white border border-slate-300 hover:bg-slate-50 text-slate-800 py-3.5 rounded-xl font-semibold transition-all hover:scale-[1.02] active:scale-[0.98]">
            🏠 Kabinetga qaytish
          </button>
          <button onClick={() => router.push(`/exams?type=${result.exam_type}`)} className="flex-1 bg-orange-600 hover:bg-orange-700 text-white py-3.5 rounded-xl font-semibold shadow-lg shadow-orange-200 transition-all hover:scale-[1.02] active:scale-[0.98]">
            🔄 Yana imtihon topshirish
          </button>
        </motion.div>
      </div>
    </main>
  );
}