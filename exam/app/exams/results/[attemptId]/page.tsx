"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
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

export default function ResultPage() {
  const router = useRouter();
  const params = useParams();
  const attemptId = Number(params.attemptId);

  const [result, setResult] = useState<ResultData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadResult();
  }, [attemptId]);

  async function loadResult() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(
        `${API_URL}/api/v2/exam/attempts/${attemptId}/result`,
        { credentials: "include" }
      );

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
        <div className="bg-white rounded-xl shadow p-8 text-center max-w-md">
          <div className="text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Xatolik</h2>
          <p className="text-slate-600 mb-6">{error}</p>
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

  if (!result) return null;

  const totalItems = result.blocks.reduce((sum, b) => sum + b.items.length, 0);
  const correctItems = result.blocks.reduce(
    (sum, b) => sum + b.items.filter((i) => i.is_correct === true).length,
    0
  );

  return (
    <main className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <button
            onClick={() => router.push("/cabinet")}
            className="text-slate-600 hover:text-slate-900"
          >
            ← Kabinetga qaytish
          </button>
          <h1 className="text-xl font-bold text-slate-900">Natija</h1>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-6">
        {/* Umumiy ball */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 mb-6 text-center">
          <div className="text-5xl mb-3">
            {result.percentage >= 70 ? "🎉" : result.percentage >= 40 ? "👍" : "💪"}
          </div>
          <h2 className="text-2xl font-bold text-slate-900 mb-1">
            {result.exam_title}
          </h2>
          <p className="text-slate-500 mb-6 capitalize">{result.exam_type} imtihoni</p>

          <div className="flex items-center justify-center gap-8 mb-6">
            <div>
              <div className="text-5xl font-bold text-emerald-600">
                {result.total_score}
              </div>
              <div className="text-sm text-slate-500 mt-1">Ball</div>
            </div>
            <div className="w-px h-16 bg-slate-200"></div>
            <div>
              <div className="text-5xl font-bold text-blue-600">
                {result.percentage}%
              </div>
              <div className="text-sm text-slate-500 mt-1">Foiz</div>
            </div>
            <div className="w-px h-16 bg-slate-200"></div>
            <div>
              <div className="text-5xl font-bold text-purple-600">
                {result.cefr_estimate}
              </div>
              <div className="text-sm text-slate-500 mt-1">CEFR daraja</div>
            </div>
          </div>

          <div className="flex items-center justify-center gap-6 text-sm">
            <span className="text-slate-600">
              📝 Jami: <strong>{totalItems}</strong>
            </span>
            <span className="text-emerald-600">
              ✅ To'g'ri: <strong>{correctItems}</strong>
            </span>
            <span className="text-red-600">
              ❌ Noto'g'ri: <strong>{totalItems - correctItems}</strong>
            </span>
          </div>
        </div>

        {/* Blocklar */}
        {result.blocks.map((block) => (
          <div
            key={block.block_id}
            className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-slate-900">{block.title}</h3>
              <span className="px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-sm font-semibold">
                Ball: {block.score}
              </span>
            </div>

            <div className="space-y-4">
              {block.items.map((item) => (
                <div
                  key={item.item_id}
                  className={`border rounded-lg p-4 ${
                    item.is_correct === true
                      ? "border-emerald-200 bg-emerald-50"
                      : item.is_correct === false
                      ? "border-red-200 bg-red-50"
                      : "border-slate-200"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-xl flex-shrink-0">
                      {item.is_correct === true
                        ? "✅"
                        : item.is_correct === false
                        ? "❌"
                        : "⚪"}
                    </span>

                    <div className="flex-1">
                      <h4 className="font-semibold text-slate-900 mb-1">
                        {item.order}. {item.question_text || item.title}
                      </h4>

                      {item.user_selected && item.user_selected.length > 0 && (
                        <p className="text-sm text-slate-600">
                          Sizning javobingiz:{" "}
                          <span
                            className={
                              item.is_correct
                                ? "text-emerald-700 font-semibold"
                                : "text-red-700 font-semibold"
                            }
                          >
                            Variant {item.user_selected.join(", ")}
                          </span>
                        </p>
                      )}

                      {item.is_correct === false &&
                        item.correct_option_ids.length > 0 && (
                          <p className="text-sm text-emerald-700 mt-1">
                            To'g'ri javob:{" "}
                            <span className="font-semibold">
                              Variant {item.correct_option_ids.join(", ")}
                            </span>
                          </p>
                        )}

                      <p className="text-xs text-slate-500 mt-2">
                        Ball: {item.final_score} / {item.max_score}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        <div className="flex gap-4 mb-12">
          <button
            onClick={() => router.push("/cabinet")}
            className="flex-1 bg-slate-200 hover:bg-slate-300 text-slate-800 py-3 rounded-lg font-semibold"
          >
            🏠 Kabinetga qaytish
          </button>
          <button
            onClick={() => router.push(`/exams?type=${result.exam_type}`)}
            className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-lg font-semibold"
          >
            🔄 Yana imtihon
          </button>
        </div>
      </div>
    </main>
  );
} 