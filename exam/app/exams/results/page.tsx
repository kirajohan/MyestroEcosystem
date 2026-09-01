"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { API_URL } from "@/lib/api";

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

const STATUS_LABELS: Record<string, string> = {
  created: "Yaratilgan",
  in_progress: "Davom etmoqda",
  submitted: "Yuborilgan",
  scoring: "Baholanmoqda",
  completed: "Yakunlangan",
  needs_review: "Tekshiruv kerak",
  failed: "Xatolik",
};

function statusClass(status: string) {
  if (status === "completed") return "bg-emerald-100 text-emerald-800";
  if (status === "in_progress") return "bg-blue-100 text-blue-800";
  if (status === "scoring") return "bg-amber-100 text-amber-800";
  if (status === "failed") return "bg-red-100 text-red-800";
  return "bg-slate-100 text-slate-700";
}

function formatDate(value: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleString("uz-UZ", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ResultsPage() {
  const router = useRouter();

  const [items, setItems] = useState<AttemptHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadResults();
  }, []);

async function loadResults() {
  setLoading(true);
  setError("");

  try {
    const res = await fetch(`${API_URL}/api/v2/exam/attempts/me`, {
      credentials: "include",
    });

    console.log("📊 Results API status:", res.status);  // ← QO'SHILDI

    if (!res.ok) {
      const errorText = await res.text();
      console.error("❌ Results API error:", errorText);  // ← QO'SHILDI
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();
    console.log("✅ Results data:", data);  // ← QO'SHILDI
    setItems(data.items || []);
  } catch (err) {
    console.error("Natijalar yuklanmadi:", err);
    setError("Natijalar yuklanmadi. Qayta login qiling.");
  } finally {
    setLoading(false);
  }
}
  function handleOpenAttempt(item: AttemptHistoryItem) {
    if (item.status === "completed") {
      router.push(`/exams/results/${item.attempt_id}`);
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

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4" />
          <p className="text-slate-500">Natijalar yuklanmoqda...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <button
            onClick={() => router.push("/cabinet")}
            className="text-slate-600 hover:text-slate-900"
          >
            ← Kabinetga qaytish
          </button>

          <h1 className="text-xl font-bold text-slate-900">
            Mening natijalarim
          </h1>
        </div>
      </header>

      <div className="max-w-5xl mx-auto p-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-6">
            ❌ {error}
          </div>
        )}

        {items.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
            <div className="text-5xl mb-4">📭</div>
            <h2 className="text-xl font-bold mb-2">Hali natijalar yo‘q</h2>
            <p className="text-slate-500 mb-6">
              Birinchi imtihonni topshiring va natijangiz shu yerda chiqadi.
            </p>
            <button
              onClick={() => router.push("/cabinet")}
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-3 rounded-lg font-semibold"
            >
              Imtihon tanlash
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {items.map((item) => (
              <div
                key={item.attempt_id}
                className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm px-2.5 py-1 rounded-full bg-slate-100 text-slate-700">
                        {TYPE_LABELS[item.exam_type] || item.exam_type}
                      </span>

                      {item.cefr_level && (
                        <span className="text-sm px-2.5 py-1 rounded-full bg-purple-100 text-purple-800 font-semibold">
                          {item.cefr_level}
                        </span>
                      )}

                      <span
                        className={`text-sm px-2.5 py-1 rounded-full font-semibold ${statusClass(
                          item.status
                        )}`}
                      >
                        {STATUS_LABELS[item.status] || item.status}
                      </span>
                    </div>

                    <h2 className="text-lg font-bold text-slate-900">
                      {item.exam_title}
                    </h2>

                    <p className="text-sm text-slate-500 mt-1">
                      Boshlangan: {formatDate(item.started_at)}
                    </p>
                  </div>

                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-emerald-600">
                        {item.total_score}/{item.max_score}
                      </div>
                      <div className="text-xs text-slate-500">Ball</div>
                    </div>

                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {item.percentage}%
                      </div>
                      <div className="text-xs text-slate-500">Foiz</div>
                    </div>

                    <button
                      onClick={() => handleOpenAttempt(item)}
                      className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-lg font-semibold"
                    >
                      {item.status === "completed"
                        ? "Natijani ko‘rish"
                        : item.status === "in_progress"
                        ? "Davom etish"
                        : "Ochish"}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}