"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { useRouter, useParams } from "next/navigation";
import { API_URL } from "@/lib/api";
import AudioPlayer from "@/components/AudioPlayer";

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
  max_score: number;
  order: number;
  options: Option[];
}

interface BlockData {
  block_id: number;
  block_type: string;
  title: string;
  instructions?: string;
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

// ═══════════════════════════════════════════════════════════
// COMPONENT
// ═══════════════════════════════════════════════════════════

export default function ExamRoomPage() {
  const router = useRouter();
  const params = useParams();
  const attemptId = Number(params.attemptId);

  // ── State ──────────────────────────────────────────────
  const [attempt, setAttempt] = useState<AttemptInfo | null>(null);
  const [blocksData, setBlocksData] = useState<Record<number, BlockData>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Navigatsiya
  const [currentBlockIndex, setCurrentBlockIndex] = useState(0);
  const [currentItemIndex, setCurrentItemIndex] = useState(0);

  // Javoblar: { item_id: [option_id, ...] }
  const [answers, setAnswers] = useState<Record<number, number[]>>({});
  const [savingItemId, setSavingItemId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Timer
  const [timeLeft, setTimeLeft] = useState<number | null>(null);

  // ── 1. Attempt yuklash ─────────────────────────────────
  useEffect(() => {
    loadAttempt();
  }, [attemptId]);

  async function loadAttempt() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/api/v2/exam/attempts/${attemptId}`, {
        credentials: "include",
      });

      if (!res.ok) {
        if (res.status === 404) throw new Error("Attempt topilmadi");
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      setAttempt(data);

      if (data.status === "completed" || data.status === "scoring") {
        router.push(`/exams/result/${attemptId}`);
        return;
      }

      // Birinchi block'ni yuklash
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
      const res = await fetch(
        `${API_URL}/api/v2/exam/attempts/${attemptId}/blocks/${blockId}`,
        { credentials: "include" }
      );

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();

      setBlocksData((prev) => ({
        ...prev,
        [blockId]: {
          block_id: blockId,
          block_type: data.block_type,
          title: data.title,
          instructions: data.instructions,
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

  // ── 5. Javob tanlash + Autosave ────────────────────────
  const handleSelectOption = useCallback(
    async (itemId: number, optionId: number) => {
      setAnswers((prev) => {
        const current = prev[itemId] || [];
        const newSelected = current.includes(optionId)
          ? current.filter((id) => id !== optionId)
          : [optionId];
        return { ...prev, [itemId]: newSelected };
      });

      setSavingItemId(itemId);
      try {
        await fetch(`${API_URL}/api/v2/exam/attempts/${attemptId}/answers`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            answers: [{ item_id: itemId, selected_options: [optionId] }],
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

  // ── 6. Submit ──────────────────────────────────────────
  async function handleSubmit(auto = false) {
    if (!auto && !confirm("Imtihonni yakunlashni xohlaysizmi?")) return;

    setSubmitting(true);
    try {
      const res = await fetch(
        `${API_URL}/api/v2/exam/attempts/${attemptId}/submit`,
        { method: "POST", credentials: "include" }
      );

      if (!res.ok) throw new Error("Submit qilinmadi");

      router.push(`/exams/result/${attemptId}`);
    } catch (err) {
      console.error("Submit xatosi:", err);
      alert("Imtihon yakunlanmadi. Qayta urinib ko'ring.");
      setSubmitting(false);
    }
  }

  // ── 7. Navigatsiya funksiyalari ────────────────────────
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
        if (prevData) {
          setCurrentItemIndex(prevData.items.length - 1);
        }
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

  // ── 8. Umumiy javob statistikasi ───────────────────────
  const totalItems = useMemo(() => {
    let count = 0;
    for (const block of attempt?.blocks || []) {
      const data = blocksData[block.block_id];
      if (data?.loaded) count += data.items.length;
    }
    return count;
  }, [attempt, blocksData]);

  const answeredCount = Object.values(answers).filter((a) => a.length > 0).length;

  // ── 9. Timer format ────────────────────────────────────
  function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  }

  // ── 10. Passage'ni topish ──────────────────────────────
  const currentPassage = useMemo(() => {
    if (!currentBlockData) return null;
    const itemWithPassage = currentBlockData.items.find((i) => i.passage_text);
    return itemWithPassage?.passage_text || null;
  }, [currentBlockData]);

  // ═══════════════════════════════════════════════════════
  // RENDER: Loading / Error
  // ═══════════════════════════════════════════════════════

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-slate-500">Imtihon yuklanmoqda...</p>
        </div>
      </main>
    );
  }

  if (error || !attempt) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
        <div className="bg-white rounded-xl shadow p-8 text-center max-w-md">
          <div className="text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Xatolik</h2>
          <p className="text-slate-600 mb-6">{error || "Attempt topilmadi"}</p>
          <button
            onClick={() => router.push("/cabinet")}
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2.5 rounded-lg font-semibold"
          >
            Kabinetga qaytish
          </button>
        </div>
      </main>
    );
  }

  // ═══════════════════════════════════════════════════════
  // RENDER: Main
  // ═══════════════════════════════════════════════════════

  return (
    <main className="min-h-screen bg-slate-100 flex flex-col">
      {/* ── HEADER ─────────────────────────────────────── */}
      <header className="bg-white border-b border-slate-200 px-4 py-3 sticky top-0 z-20 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📖</span>
            <div>
              <h1 className="font-bold text-slate-900 text-sm md:text-base">
                {currentBlockData?.title || "Imtihon"}
              </h1>
              <p className="text-xs text-slate-500">
                Javob berildi: {answeredCount} / {totalItems || "..."}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {timeLeft !== null && (
              <div
                className={`px-3 py-1.5 rounded-lg font-mono text-sm md:text-lg font-bold ${
                  timeLeft < 60
                    ? "bg-red-100 text-red-700 animate-pulse"
                    : timeLeft < 300
                    ? "bg-amber-100 text-amber-700"
                    : "bg-emerald-100 text-emerald-700"
                }`}
              >
                ⏱️ {formatTime(timeLeft)}
              </div>
            )}

            <button
              onClick={() => handleSubmit()}
              disabled={submitting}
              className={`px-3 md:px-4 py-1.5 md:py-2 rounded-lg text-sm font-semibold transition-colors ${
                submitting
                  ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700 text-white"
              }`}
            >
              {submitting ? "..." : "🏁 Yakunlash"}
            </button>
          </div>
        </div>
      </header>

      {/* ── MAIN CONTENT: 2 ustun ──────────────────────── */}
      <div className="flex-1 max-w-7xl mx-auto w-full p-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* ═══ CHAP USTUN: PASSAGE yoki AUDIO ═══ */}
        <div className="lg:sticky lg:top-20 lg:self-start">
          {currentPassage ? (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 max-h-[calc(100vh-120px)] overflow-y-auto">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                📖 Passage
              </h3>
              <p className="text-slate-800 leading-relaxed whitespace-pre-line text-[15px]">
                {currentPassage}
              </p>
            </div>
          ) : currentItem?.audio_url ? (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="text-xs font-bold text-blue-600 uppercase tracking-widest mb-4 flex items-center gap-2">
                🎧 Audio
              </h3>
              <AudioPlayer audioUrl={currentItem.audio_url} />
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 text-center">
              <div className="text-4xl mb-3">📄</div>
              <p className="text-slate-400">Bu bo'limda kontent yo'q</p>
            </div>
          )}
        </div>

        {/* ═══ O'NG USTUN: NAVIGATSIYA + SAVOL ═══ */}
        <div className="space-y-4">
          {/* ── Navigatsiya paneli ─────────────────────── */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
            <div className="mb-4">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                Bloklar
              </h4>
              <div className="flex flex-wrap gap-2">
                {attempt.blocks.map((block, idx) => (
                  <button
                    key={block.block_id}
                    onClick={() => switchToBlock(idx)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      idx === currentBlockIndex
                        ? "bg-emerald-600 text-white shadow"
                        : blocksData[block.block_id]?.loaded
                        ? "bg-emerald-50 text-emerald-700 hover:bg-emerald-100"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                  >
                    {idx === currentBlockIndex ? "● " : "○ "}
                    {block.title}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                Savollar
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {currentItems.map((item, idx) => {
                  const isAnswered = (answers[item.id] || []).length > 0;
                  const isCurrent = idx === currentItemIndex;

                  return (
                    <button
                      key={item.id}
                      onClick={() => setCurrentItemIndex(idx)}
                      className={`w-9 h-9 rounded-lg text-sm font-bold transition-all ${
                        isCurrent
                          ? "bg-blue-600 text-white ring-2 ring-blue-300 scale-110"
                          : isAnswered
                          ? "bg-emerald-100 text-emerald-800 hover:bg-emerald-200"
                          : "bg-slate-100 text-slate-500 hover:bg-slate-200"
                      }`}
                    >
                      {idx + 1}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* ── Savol kartochkasi ──────────────────────── */}
          {currentItem ? (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                  Savol {currentItemIndex + 1} / {currentItems.length}
                </span>
                {savingItemId === currentItem.id && (
                  <span className="text-xs text-slate-400 animate-pulse">💾 Saqlanmoqda...</span>
                )}
              </div>

              <h3 className="text-lg font-bold text-slate-900 mb-5 leading-snug">
                {currentItem.question_text || currentItem.title}
              </h3>

              {currentItem.options.length > 0 ? (
                <div className="space-y-2.5">
                  {currentItem.options.map((option, idx) => {
                    const isSelected = answers[currentItem.id]?.includes(option.id);
                    const letter = String.fromCharCode(65 + idx);

                    return (
                      <button
                        key={option.id}
                        onClick={() => handleSelectOption(currentItem.id, option.id)}
                        className={`w-full flex items-center gap-3 p-3.5 rounded-xl border-2 transition-all text-left ${
                          isSelected
                            ? "border-emerald-500 bg-emerald-50 shadow-sm"
                            : "border-slate-200 hover:border-slate-300 hover:bg-slate-50"
                        }`}
                      >
                        <span
                          className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 transition-colors ${
                            isSelected
                              ? "bg-emerald-500 text-white"
                              : "bg-slate-200 text-slate-700"
                          }`}
                        >
                          {letter}
                        </span>
                        <span className="flex-1 text-slate-800 text-sm md:text-base">
                          {option.text}
                        </span>
                        {isSelected && <span className="text-emerald-600 font-bold text-lg">✓</span>}
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400">
                  Bu savolda variantlar yo'q
                </div>
              )}

              <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-100">
                <button
                  onClick={goToPrevItem}
                  disabled={currentBlockIndex === 0 && currentItemIndex === 0}
                  className={`px-5 py-2.5 rounded-lg font-semibold text-sm transition-colors ${
                    currentBlockIndex === 0 && currentItemIndex === 0
                      ? "bg-slate-100 text-slate-400 cursor-not-allowed"
                      : "bg-slate-200 hover:bg-slate-300 text-slate-800"
                  }`}
                >
                  ◀ Oldingi
                </button>

                {isLastItem ? (
                  <button
                    onClick={() => handleSubmit()}
                    disabled={submitting}
                    className={`px-5 py-2.5 rounded-lg font-semibold text-sm transition-colors ${
                      submitting
                        ? "bg-slate-300 text-slate-500"
                        : "bg-blue-600 hover:bg-blue-700 text-white"
                    }`}
                  >
                    {submitting ? "Yakunlanmoqda..." : "🏁 Yakunlash"}
                  </button>
                ) : (
                  <button
                    onClick={goToNextItem}
                    className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-semibold text-sm transition-colors"
                  >
                    Keyingi ▶
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center text-slate-400">
              {currentBlockData?.loaded ? "Savollar yo'q" : "Yuklanmoqda..."}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}   