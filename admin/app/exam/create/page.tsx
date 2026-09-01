"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

const EXAM_TYPES = [
  { value: "full", label: "🎯 Full Exam (To'liq sikl)" },
  { value: "listening", label: "🎧 Listening (Tinglash)" },
  { value: "reading", label: "📖 Reading (O'qish)" },
  { value: "writing", label: "✍️ Writing (Yozish)" },
  { value: "speaking", label: "🎤 Speaking (Gapirish)" },
];

const CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];

export default function CreateExamPage() {
  const router = useRouter();
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [timeLimitMin, setTimeLimitMin] = useState(10);

  const [formData, setFormData] = useState({
    code: "",
    title: "",
    description: "",
    exam_type: "reading",
    cefr_level: "A2",
    is_published: false,
  });

  function generateCode() {
    const code = `${formData.exam_type}_${formData.cefr_level.toLowerCase()}_${Date.now().toString(36).slice(-4)}`;
    setFormData((prev) => ({ ...prev, code }));
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (!token) {
        setError("Token topilmadi. Qayta login qiling.");
        return;
      }

      const res = await fetch(`${API_URL}/api/v2/exam/admin/exams`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...formData,
          time_limit_sec: timeLimitMin * 60,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `HTTP ${res.status}`);
      }

      const created = await res.json();
      alert(`✅ Exam yaratildi!\nID: ${created.id}\nCode: ${created.code}`);
      router.push("/exam/exams");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Noma'lum xato");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <button onClick={() => router.back()} className="text-blue-600 mb-2">← Orqaga</button>
      <h1 className="text-3xl font-bold mb-6">Yangi Exam yaratish</h1>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-5">
        <div className="flex gap-2 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1.5">Kod *</label>
            <input
              type="text"
              name="code"
              value={formData.code}
              onChange={handleChange}
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
            />
          </div>
          <button
            type="button"
            onClick={generateCode}
            className="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm"
          >
            🎲 Auto
          </button>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1.5">Nomi *</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1.5">Tavsif</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={3}
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Turi *</label>
            <select
              name="exam_type"
              value={formData.exam_type}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
            >
              {EXAM_TYPES.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">CEFR daraja *</label>
            <select
              name="cefr_level"
              value={formData.cefr_level}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
            >
              {CEFR_LEVELS.map((l) => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1.5">Vaqt (daqiqa) *</label>
          <input
            type="number"
            value={timeLimitMin}
            onChange={(e) => setTimeLimitMin(Number(e.target.value))}
            min={1}
            max={300}
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="is_published"
            name="is_published"
            checked={formData.is_published}
            onChange={handleChange}
          />
          <label htmlFor="is_published" className="text-sm font-medium">
            Darhol publish qilish
          </label>
        </div>

        {error && <div className="bg-red-50 text-red-600 p-4 rounded-lg">❌ {error}</div>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold"
        >
          {loading ? "Yaratilmoqda..." : "✅ Exam yaratish"}
        </button>
      </form>
    </div>
  );
}