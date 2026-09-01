"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";


interface Exam {
  id: number;
  code: string;
  title: string;
  description: string | null;
  exam_type: string;
  cefr_level: string | null;
  time_limit_sec: number;
}

const TYPE_INFO: Record<string, { icon: string; label: string; color: string }> = {
  full: { icon: "🎯", label: "Full Exam", color: "bg-indigo-500" },
  listening: { icon: "🎧", label: "Listening", color: "bg-blue-500" },
  reading: { icon: "📖", label: "Reading", color: "bg-emerald-500" },
  writing: { icon: "✍️", label: "Writing", color: "bg-amber-500" },
  speaking: { icon: "🎤", label: "Speaking", color: "bg-rose-500" },
};

function ExamsContent() {
  const router = useRouter();
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
      const res = await fetch(`${API_URL}/api/v2/exam/exams?type=${type}`, {
        credentials: "include",
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      setExams(data.items || []);
    } catch (err) {
      console.error("Exam'lar yuklanmadi:", err);
      setError("Exam'lar yuklanmadi. Qayta login qiling.");
    } finally {
      setLoading(false);
    }
  }

  async function handleStart(examId: number) {
    setStarting(examId);
    setError("");

    try {
      const res = await fetch(`${API_URL}/api/v2/exam/exams/${examId}/attempts`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      // Attempt yaratildi → imtihon xonasiga o'tamiz
      router.push(`/exams/${data.attempt_id}`);
    } catch (err) {
      console.error("Attempt yaratish xatosi:", err);
      setError(err instanceof Error ? err.message : "Imtihon boshlanmadi");
      setStarting(null);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-slate-500">Yuklanmoqda...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <button
            onClick={() => router.push("/cabinet")}
            className="text-slate-600 hover:text-slate-900 flex items-center gap-2"
          >
            ← Kabinetga qaytish
          </button>
          <h1 className="text-xl font-bold text-slate-900">Maestro Exam</h1>
        </div>
      </header>

      <div className="max-w-5xl mx-auto p-6">
        {/* Title */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className={`w-12 h-12 ${typeInfo.color} rounded-xl flex items-center justify-center text-2xl`}>
              {typeInfo.icon}
            </div>
            <div>
              <h2 className="text-3xl font-bold">{typeInfo.label}</h2>
              <p className="text-slate-500">
                {exams.length} ta imtihon mavjud
              </p>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-6">
            ❌ {error}
          </div>
        )}

        {/* Exam cards */}
        {exams.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
            <div className="text-5xl mb-4">📭</div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              Hali imtihonlar yo'q
            </h3>
            <p className="text-slate-500">
              Bu bo'limda imtihonlar tez orada paydo bo'ladi.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {exams.map((exam) => (
              <div
                key={exam.id}
                className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow"
              >
                {/* Exam info */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-slate-900 mb-1">
                      {exam.title}
                    </h3>
                    <div className="flex items-center gap-2 mb-3">
                      {exam.cefr_level && (
                        <span className="px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-full text-xs font-semibold">
                          {exam.cefr_level}
                        </span>
                      )}
                      <span className="px-2.5 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-medium">
                        ⏱️ {Math.floor(exam.time_limit_sec / 60)} daqiqa
                      </span>
                    </div>
                  </div>
                  <div className={`w-10 h-10 ${typeInfo.color} rounded-lg flex items-center justify-center text-xl`}>
                    {typeInfo.icon}
                  </div>
                </div>

                {/* Description */}
                {exam.description && (
                  <p className="text-sm text-slate-600 mb-4 line-clamp-2">
                    {exam.description}
                  </p>
                )}

                {/* Start button */}
                <button
                  onClick={() => handleStart(exam.id)}
                  disabled={starting === exam.id}
                  className={`w-full py-3 rounded-lg font-semibold transition-colors ${
                    starting === exam.id
                      ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                      : "bg-emerald-600 hover:bg-emerald-700 text-white"
                  }`}
                >
                  {starting === exam.id ? "Boshlanmoqda..." : "🚀 Imtihonni boshlash"}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

export default function ExamsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Yuklanmoqda...</div>}>
      <ExamsContent />
    </Suspense>
  );
}