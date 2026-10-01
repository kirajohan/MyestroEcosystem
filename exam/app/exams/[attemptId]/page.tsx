"use client";

import { useEffect, useState, useCallback, useMemo, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion } from "framer-motion";
import { apiFetch } from "@/lib/session";
import AudioPlayer from "@/components/AudioPlayer";
import QuestionCard from "@/components/exam/QuestionCard";
import ReadingPassage from "@/components/exam/reading/ReadingPassage";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://myestroeco-backend-production.up.railway.app";

// ═══════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════

interface Option {
  id: number;
  text: string;
  order: number;
}

interface Item {
  id: number;
  item_type: string;
  title: string;
  instruction?: string;
  question_text?: string;
  passage_text?: string;
  audio_url?: string;
  min_words?: number;
  max_words?: number;
  max_score: number;
  order: number;
  options: Option[];
}

interface BlockData {
  block_id: number;
  block_type: string;
  title: string;
  instructions?: string;
  passage_text?: string;
  audio_url?: string;
  time_limit_sec: number;
  items: Item[];
  loaded: boolean;
}

interface AttemptBlock {
  attempt_block_id: number;
  block_id: number;
  block_type: string;
  title: string;
  status: string;
}

interface AttemptInfo {
  id: number;
  exam_id: number;
  status: string;
  started_at?: string;
  deadline?: string;
  blocks: AttemptBlock[];
}

interface AnswerData {
  selected_options: number[];
  text_answer: string;
}

// ═══════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════

export default function ExamRoomPage() {
  const router = useRouter();
  const params = useParams();
  const attemptId = Number(params.attemptId);

  // ── Asosiy state ──────────────────────────────────────
  const [attempt, setAttempt] = useState<AttemptInfo | null>(null);
  const [blocksData, setBlocksData] = useState<Record<number, BlockData>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Navigatsiya
  const [currentBlockIndex, setCurrentBlockIndex] = useState(0);
  const [currentItemIndex, setCurrentItemIndex] = useState(0);

  // Javoblar — yangi struktura: { item_id: { selected_options: [], text_answer: "" } }
  const [answers, setAnswers] = useState<Record<number, AnswerData>>({});
  const [savingItemId, setSavingItemId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Timer
  const [timeLeft, setTimeLeft] = useState<number | null>(null);

  // ── Split-pane resizer (Reading/Writing uchun) ────────
  const [leftPct, setLeftPct] = useState(50);
  const [isDesktop, setIsDesktop] = useState(false);
  const gridRef = useRef<HTMLDivElement>(null);
  const draggingRef = useRef(false);

  useEffect(() => {
    const mq = window.matchMedia("(min-width: 1024px)");
    const update = () => setIsDesktop(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);

  const startDrag = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    draggingRef.current = true;

    const move = (ev: MouseEvent) => {
      if (!draggingRef.current) return;
      const rect = gridRef.current?.getBoundingClientRect();
      if (!rect) return;
      const pct = ((ev.clientX - rect.left) / rect.width) * 100;
      setLeftPct(Math.min(70, Math.max(30, pct)));
    };

    const up = () => {
      draggingRef.current = false;
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", up);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };

    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", up);
  }, []);

  // ── 1. Attempt yuklash ─────────────────────────────────
  useEffect(() => {
    loadAttempt();
  }, [attemptId]);

  async function loadAttempt() {
    setLoading(true);
    setError("");
    try {
      const res = await apiFetch(`/api/v2/exam/attempts/${attemptId}`);

      if (!res.ok) {
        if (res.status === 404) throw new Error("Attempt topilmadi");
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      setAttempt(data);

      if (data.status === "completed" || data.status === "scoring") {
        router.push(`/exams/results/${attemptId}`);
        return;
      }

      if (data.blocks && data.blocks.length > 0) {
        await loadBlock(data.blocks[0].block_id);
      } else {
        setError("Bu imtihonda block'lar yo'q");
      }
    } catch (err) {
      console.error("Attempt yuklanmadi:", err);
      setError(err instanceof Error ? err.message : "Attempt yuklanmadi");
    } finally {
      setLoading(false);
    }
  }

  // ── 2. Block yuklash ───────────────────────────────────
  async function loadBlock(blockId: number) {
    if (blocksData[blockId]?.loaded) return;

    try {
      // ✅ TO'G'RI: Student uchun maxsus, xavfsiz endpoint ishlatilmoqda
      const res = await apiFetch(`/api/v2/exam/attempts/${attemptId}/blocks/${blockId}`);

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      setBlocksData((prev) => ({
        ...prev,
        [blockId]: {
          block_id: blockId,
          block_type: data.block_type,
          title: data.title,
          instructions: data.instructions,
          passage_text: data.passage_text,
          audio_url: data.audio_url,
          time_limit_sec: data.time_limit_sec,
          items: data.items || [],
          loaded: true,
        },
      }));
    } catch (err) {
      console.error("Block yuklanmadi:", err);
    }
  }

  // ── 3. Block'ga o'tish ─────────────────────────────────
  const switchToBlock = useCallback(
    async (blockIndex: number) => {
      if (!attempt) return;
      const block = attempt.blocks[blockIndex];
      if (!block) return;
      setCurrentBlockIndex(blockIndex);
      setCurrentItemIndex(0);
      await loadBlock(block.block_id);
    },
    [attempt, blocksData]
  );

  // ── 4. Timer ───────────────────────────────────────────
  useEffect(() => {
    if (!attempt?.deadline) return;

    const interval = setInterval(() => {
      const deadline = new Date(attempt.deadline!).getTime();
      const now = Date.now();
      const remaining = Math.max(0, Math.floor((deadline - now) / 1000));
      setTimeLeft(remaining);
      if (remaining <= 0) {
        clearInterval(interval);
        handleSubmit(true);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [attempt?.deadline]);

  // ── 5. Javob tanlash (Reading/Listening) + Autosave ────
const handleSelectOption = useCallback(
  async (itemId: number, optionId: number) => {
    let finalSelected: number[] = [];

    setAnswers((prev) => {
      const current = prev[itemId] || { selected_options: [], text_answer: "" };
      // ✅ Faqat BITTA javob tanlash mumkin
      const newSelected = current.selected_options.includes(optionId)
        ? []          // Xuddi shu option'ga qayta bosilsa → bekor qilish
        : [optionId]; // Boshqa option bosilsa → faqat shuni qoldirish
      finalSelected = newSelected;
      return { ...prev, [itemId]: { ...current, selected_options: newSelected } };
    });

    setSavingItemId(itemId);
    try {
      // ✅ Serverga ham to'g'ri qiymat yuboriladi (toggle-off'da bo'sh array)
      await apiFetch(`/api/v2/exam/attempts/${attemptId}/answers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          answers: [{ item_id: itemId, selected_options: finalSelected }],
        }),
      });
    } catch (err) {
      console.error("Javob saqlanmadi:", err);
    } finally {
      setSavingItemId(null);
    }
  },
  [attemptId]
);  

  // ── 6. Writing answer saqlash (autosave) ──────────────
  const handleSaveText = useCallback(
    async (itemId: number, text: string) => {
      setAnswers((prev) => {
        const current = prev[itemId] || { selected_options: [], text_answer: "" };
        return { ...prev, [itemId]: { ...current, text_answer: text } };
      });

      setSavingItemId(itemId);
      try {
        await apiFetch(`/api/v2/exam/attempts/${attemptId}/answers`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            answers: [{ item_id: itemId, text_answer: text }],
          }),
        });
      } catch (err) {
        console.error("Writing answer saqlanmadi:", err);
      } finally {
        setSavingItemId(null);
      }
    },
    [attemptId]
  );

  // ── 7. Submit ──────────────────────────────────────────
  async function handleSubmit(auto = false) {
    if (!auto && !confirm("Imtihonni yakunlashni xohlaysizmi?")) return;
    setSubmitting(true);
    try {
      const res = await apiFetch(`/api/v2/exam/attempts/${attemptId}/submit`, {
        method: "POST",
      });
      if (!res.ok) throw new Error("Submit qilinmadi");
      router.push(`/exams/results/${attemptId}`);
    } catch (err) {
      console.error("Submit xatosi:", err);
      alert("Imtihon yakunlanmadi. Qayta urinib ko'ring.");
      setSubmitting(false);
    }
  }

  // ── 8. Navigatsiya ─────────────────────────────────────
  const currentBlock = attempt?.blocks[currentBlockIndex];
  const currentBlockData = currentBlock ? blocksData[currentBlock.block_id] : null;
  const currentItems = currentBlockData?.items || [];
  const currentItem = currentItems[currentItemIndex];

  const goToPrevItem = () => {
    if (currentItemIndex > 0) {
      setCurrentItemIndex((i) => i - 1);
    } else if (currentBlockIndex > 0) {
      const prevBlockIndex = currentBlockIndex - 1;
      const prevBlock = attempt?.blocks[prevBlockIndex];
      if (prevBlock) {
        switchToBlock(prevBlockIndex);
        const prevData = blocksData[prevBlock.block_id];
        if (prevData) setCurrentItemIndex(prevData.items.length - 1);
      }
    }
  };

  const goToNextItem = () => {
    if (currentItemIndex < currentItems.length - 1) {
      setCurrentItemIndex((i) => i + 1);
    } else if (currentBlockIndex < (attempt?.blocks.length || 0) - 1) {
      switchToBlock(currentBlockIndex + 1);
    }
  };

  const isLastItem =
    currentBlockIndex === (attempt?.blocks.length || 0) - 1 &&
    currentItemIndex === currentItems.length - 1;

  // ── 9. Umumiy statistika ───────────────────────────────
  const totalItems = useMemo(() => {
    let count = 0;
    for (const block of attempt?.blocks || []) {
      const data = blocksData[block.block_id];
      if (data?.loaded) count += data.items.length;
    }
    return count;
  }, [attempt, blocksData]);

  const answeredCount = Object.values(answers).filter(
    (a) => a.selected_options.length > 0 || (a.text_answer && a.text_answer.trim().length > 0)
  ).length;

  function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  }

  // ═══════════════════════════════════════════════════════
  // RENDER: Loading
  // ═══════════════════════════════════════════════════════

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 via-orange-50 to-rose-50">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 mx-auto mb-4 rounded-full border-4 border-orange-200 border-t-orange-600"
          />
          <p className="text-slate-600 font-medium">Imtihon yuklanmoqda...</p>
        </motion.div>
      </main>
    );
  }

  // ═══════════════════════════════════════════════════════
  // RENDER: Error
  // ═══════════════════════════════════════════════════════

  if (error || !attempt) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 via-orange-50 to-rose-50 p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-2xl p-8 text-center max-w-md border border-white/50"
        >
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Xatolik</h2>
          <p className="text-slate-600 mb-6">{error || "Attempt topilmadi"}</p>
          <button
            onClick={() => router.push("/cabinet")}
            className="bg-gradient-to-r from-orange-600 to-rose-500 text-white px-6 py-2.5 rounded-lg font-semibold"
          >
            Kabinetga qaytish
          </button>
        </motion.div>
      </main>
    );
  }

  // ═══════════════════════════════════════════════════════
  // RENDER: Main
  // ═══════════════════════════════════════════════════════

  const isListening = currentBlockData?.block_type === "listening";
  const isReading = currentBlockData?.block_type === "reading";
  const isWriting = currentBlockData?.block_type === "writing";
  
  // ✅ YANGI: Writing uchun ham split-pane yoqiladi
  const useSplitPane = (isReading || isWriting) && isDesktop;

  // ✅ YANGI: Content mavjudligini tekshirish
  const hasContent = !!(currentBlockData?.passage_text || currentBlockData?.audio_url);
  const hasInstructions = !!(currentBlockData?.instructions);
  const showNavigator = currentItems.length > 1; // ✅ Writing'da 1 ta item bo'lsa navigator yashiriladi

  return (
    <main className="min-h-screen flex flex-col bg-gradient-to-br from-slate-100 via-orange-50 to-rose-50 relative overflow-hidden">
      {/* Background decorative blobs */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-0 w-96 h-96 bg-orange-200/30 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-rose-200/30 rounded-full blur-3xl" />
      </div>

      {/* ═══ HEADER ═══ */}
      <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-xl border-b border-slate-200/50 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: isListening && currentItem ? [0, 5, -5, 0] : 0 }}
              transition={{ duration: 2, repeat: Infinity }}
              className="text-2xl"
            >
              {isListening ? "🎧" : isReading ? "📖" : isWriting ? "✍️" : "📝"}
            </motion.div>
            <div>
              <h1 className="font-bold text-slate-900 text-sm md:text-base">
                {currentBlockData?.title || "Imtihon"}
              </h1>
              <p className="text-xs text-slate-500">
                Javob berildi:{" "}
                <span className="font-semibold text-emerald-600">{answeredCount}</span> /{" "}
                {totalItems || "..."}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {timeLeft !== null && (
              <motion.div
                animate={timeLeft < 60 ? { scale: [1, 1.05, 1] } : {}}
                transition={{ duration: 1, repeat: timeLeft < 60 ? Infinity : 0 }}
                className={`px-4 py-2 rounded-xl font-mono text-sm md:text-lg font-bold backdrop-blur-sm border ${
                  timeLeft < 60
                    ? "bg-red-100/80 text-red-700 border-red-200"
                    : timeLeft < 300
                    ? "bg-amber-100/80 text-amber-700 border-amber-200"
                    : "bg-emerald-100/80 text-emerald-700 border-emerald-200"
                }`}
              >
                ⏱️ {formatTime(timeLeft)}
              </motion.div>
            )}

            <motion.button
              onClick={() => handleSubmit()}
              disabled={submitting}
              whileHover={{ scale: submitting ? 1 : 1.05 }}
              whileTap={{ scale: submitting ? 1 : 0.95 }}
              className={`px-4 md:px-5 py-2 rounded-xl text-sm font-semibold transition-colors ${
                submitting
                  ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                  : "bg-gradient-to-r from-orange-600 to-rose-500 hover:shadow-lg text-white"
              }`}
            >
              {submitting ? "..." : "🏁 Yakunlash"}
            </motion.button>
          </div>
        </div>
      </header>

      {/* ═══ MAIN CONTENT ═══ */}
      <div
        ref={gridRef}
        className={`relative z-10 flex-1 max-w-7xl mx-auto w-full p-4 grid grid-cols-1 lg:grid-cols-2 gap-4 ${
          useSplitPane ? "lg:gap-0" : ""
        }`}
        style={
          useSplitPane
            ? { gridTemplateColumns: `${leftPct}fr 16px ${100 - leftPct}fr` }
            : undefined
        }
      >
        {/* ═══ LEFT COLUMN: CONTENT (Passage / Audio / Instructions) ═══ */}
        <div className="lg:sticky lg:top-20 lg:self-start space-y-4 min-w-0">
          {/* Block Tabs */}
          {attempt.blocks.length > 1 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/80 backdrop-blur-xl rounded-2xl border border-slate-200/50 shadow-sm p-3"
            >
              <div className="flex flex-wrap gap-2">
                {attempt.blocks.map((block, idx) => (
                  <motion.button
                    key={block.block_id}
                    onClick={() => switchToBlock(idx)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`relative px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                      idx === currentBlockIndex
                        ? "bg-gradient-to-r from-orange-500 to-rose-500 text-white shadow-md"
                        : "bg-white/50 text-slate-600 hover:bg-white"
                    }`}
                  >
                    {idx === currentBlockIndex ? "● " : "○ "}
                    {block.title}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}

          {/* Content Area — ✅ "Kontent yo'q" fallback OLINDI */}
          {currentBlockData?.passage_text ? (
            <ReadingPassage
              text={currentBlockData.passage_text}
              title={currentBlockData.title}
              instruction={currentBlockData.instructions}
            />
          ) : currentBlockData?.audio_url ? (
            <AudioPlayer
              audioUrl={currentBlockData.audio_url}
              maxListens={3}
              title={currentBlockData.title}
            />
          ) : null}

          {/* Instructions — ✅ Faqat content yo'q bo'lsa yoki Writing uchun ko'rsatiladi */}
          {hasInstructions && (!hasContent || isWriting) && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className={`backdrop-blur-xl rounded-2xl border p-6 ${
                isWriting
                  ? "bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200"
                  : "bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200"
              }`}
            >
              <div className={`text-xs font-bold uppercase tracking-widest mb-3 ${
                isWriting ? "text-purple-700" : "text-blue-700"
              }`}>
                {isWriting ? "✍️ Writing Task" : "📋 Instructions"}
              </div>
              <p className={`leading-relaxed ${
                isWriting ? "text-purple-900 text-base" : "text-blue-900 text-sm"
              }`}>
                {currentBlockData.instructions}
              </p>
            </motion.div>
          )}
        </div>

        {/* ═══ SPLIT-PANE DIVIDER (Reading + Writing + Desktop) ═══ */}
        {useSplitPane && (
          <div
            onMouseDown={startDrag}
            className="hidden lg:flex items-center justify-center cursor-col-resize group select-none"
            title="Ustunlar kengligini sozlash"
          >
            <div className="w-1.5 h-28 rounded-full bg-slate-300 group-hover:bg-orange-500 group-active:bg-orange-600 transition-colors" />
          </div>
        )}

        {/* ═══ RIGHT COLUMN: QUESTIONS ═══ */}
        <div className="space-y-4 min-w-0">
          {/* Question Navigation — ✅ Faqat 1 tadan ko'p item bo'lsa ko'rinadi */}
          {showNavigator && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/80 backdrop-blur-xl rounded-2xl border border-slate-200/50 shadow-xl p-4"
            >
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">
                Question Navigator
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {currentItems.map((item, idx) => {
                  const answer = answers[item.id];
                  const isAnswered = answer && (
                    answer.selected_options.length > 0 || 
                    (answer.text_answer && answer.text_answer.trim().length > 0)
                  );
                  const isCurrent = idx === currentItemIndex;

                  return (
                    <motion.button
                      key={item.id}
                      onClick={() => setCurrentItemIndex(idx)}
                      whileHover={{ scale: 1.1, y: -2 }}
                      whileTap={{ scale: 0.95 }}
                      className={`relative w-10 h-10 rounded-xl text-sm font-bold transition-all shadow-sm ${
                        isCurrent
                          ? "bg-gradient-to-br from-orange-500 to-rose-500 text-white ring-4 ring-orange-200 scale-110"
                          : isAnswered
                          ? "bg-gradient-to-br from-emerald-500 to-teal-500 text-white"
                          : "bg-white text-slate-600 hover:bg-slate-50 border border-slate-200"
                      }`}
                    >
                      {idx + 1}
                      {isAnswered && !isCurrent && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full border-2 border-white"
                        />
                      )}
                    </motion.button>
                  );
                })}
              </div>

              {/* Progress bar */}
              <div className="mt-4 h-2 bg-slate-100 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full"
                  animate={{
                    width: `${(answeredCount / (totalItems || 1)) * 100}%`,
                  }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </motion.div>
          )}

          {/* Current Question */}
          {currentItem ? (
            <QuestionCard
              item={currentItem}
              itemIndex={currentItemIndex}
              totalItems={currentItems.length}
              attemptId={attemptId}                    // ← YANGI
              apiUrl={API_URL}                         // ← YANGI
              selectedOptions={answers[currentItem.id]?.selected_options || []}
              onSelectOption={handleSelectOption}
              onSaveText={handleSaveText}
              textAnswer={answers[currentItem.id]?.text_answer || ""}
              isSaving={savingItemId === currentItem.id}
            />
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white/80 backdrop-blur-xl rounded-2xl border border-slate-200/50 shadow-xl p-12 text-center"
            >
              <div className="text-5xl mb-3">📝</div>
              <p className="text-slate-500">
                {currentBlockData?.loaded ? "Savollar yo'q" : "Yuklanmoqda..."}
              </p>
            </motion.div>
          )}

          {/* Navigation Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between gap-3"
          >
            <motion.button
              onClick={goToPrevItem}
              disabled={currentBlockIndex === 0 && currentItemIndex === 0}
              whileHover={{ scale: currentBlockIndex === 0 && currentItemIndex === 0 ? 1 : 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`flex-1 px-5 py-3 rounded-xl font-semibold text-sm transition-all ${
                currentBlockIndex === 0 && currentItemIndex === 0
                  ? "bg-slate-100 text-slate-400 cursor-not-allowed"
                  : "bg-white text-slate-800 hover:bg-slate-50 shadow-md border border-slate-200"
              }`}
            >
              ◀ Oldingi
            </motion.button>

            {isLastItem ? (
              <motion.button
                onClick={() => handleSubmit()}
                disabled={submitting}
                whileHover={{ scale: submitting ? 1 : 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`flex-1 px-5 py-3 rounded-xl font-semibold text-sm transition-all ${
                  submitting
                    ? "bg-slate-300 text-slate-500"
                    : "bg-gradient-to-r from-orange-600 to-rose-500 text-white shadow-lg hover:shadow-xl"
                }`}
              >
                {submitting ? "Yakunlanmoqda..." : "🏁 Yakunlash"}
              </motion.button>
            ) : (
              <motion.button
                onClick={goToNextItem}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex-1 px-5 py-3 bg-gradient-to-r from-emerald-600 to-teal-500 hover:shadow-lg text-white rounded-xl font-semibold text-sm shadow-md transition-all"
              >
                Keyingi ▶
              </motion.button>
            )}
          </motion.div>
        </div>
      </div>
    </main>
  );
}