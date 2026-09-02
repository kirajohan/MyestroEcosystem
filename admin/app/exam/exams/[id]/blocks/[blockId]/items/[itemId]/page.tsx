"use client";

import { useEffect, useState, FormEvent } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import AudioUpload from "@/app/exam/components/AudioUpload";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

interface Option {
  id?: number;
  text: string;
  is_correct: boolean;
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
  answer_key?: any;
}

export default function ItemEditPage() {
  const router = useRouter();
  const params = useParams();
  const examId = Number(params.id);
  const blockId = Number(params.blockId);
  const itemId = params.itemId === "new" ? null : Number(params.itemId);
  const { token } = useAuth();

  const [loading, setLoading] = useState(!!itemId);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    item_type: "reading_question",
    title: "",
    instruction: "",
    question_text: "",
    passage_text: "",
    audio_url: "",
    max_score: 1,
    order: 1,
  });

  const [options, setOptions] = useState<Option[]>([
    { text: "", is_correct: false, order: 1 },
    { text: "", is_correct: false, order: 2 },
    { text: "", is_correct: false, order: 3 },
    { text: "", is_correct: false, order: 4 },
  ]);

  const loadItem = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${API_URL}/api/v2/exam/admin/blocks/${blockId}/items`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!res.ok) throw new Error("Yuklanmadi");
      const items = await res.json();
      const item = items.find((i: Item) => i.id === itemId);
      if (item) {
        setFormData({
          item_type: item.item_type,
          title: item.title || "",
          instruction: item.instruction || "",
          question_text: item.question_text || "",
          passage_text: item.passage_text || "",
          audio_url: item.audio_url || "",
          max_score: item.max_score || 1,
          order: item.order || 1,
        });
        if (item.options && item.options.length > 0) {
          setOptions(item.options.map((o: Option) => ({ ...o })));
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Xato");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (itemId && token) loadItem();
  }, [itemId, token]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "number" ? Number(value) : value,
    }));
  }

  function handleOptionChange(idx: number, field: "text" | "is_correct", value: string | boolean) {
    setOptions((prev) =>
      prev.map((opt, i) =>
        i === idx ? { ...opt, [field]: value } : opt
      )
    );
  }

  function handleAddOption() {
    setOptions((prev) => [
      ...prev,
      { text: "", is_correct: false, order: prev.length + 1 },
    ]);
  }

  function handleRemoveOption(idx: number) {
    setOptions((prev) => prev.filter((_, i) => i !== idx));
  }

  function handleAudioUploaded(url: string) {
    setFormData((prev) => ({ ...prev, audio_url: url }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");

    try {
      // answer_key tayyorlash
      const correctIds = options
        .map((opt, idx) => (opt.is_correct ? idx + 1 : null))
        .filter((id) => id !== null);

      const payload = {
        ...formData,
        audio_file_id: formData.audio_url,  // audio_url o'rniga audio_file_id
        audio_url: null,  // Eski maydonni tozalash
        options: options.filter((o) => o.text.trim()),
        answer_key: { correct_option_ids: correctIds },
      };

      const url = itemId
        ? `${API_URL}/api/v2/exam/admin/items/${itemId}`
        : `${API_URL}/api/v2/exam/admin/blocks/${blockId}/items`;
      const method = itemId ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `HTTP ${res.status}`);
      }

      alert(itemId ? "✅ Savol yangilandi" : "✅ Savol yaratildi");
      router.push(`/exam/exams/${examId}/blocks/${blockId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Saqlashda xato");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="p-6">Yuklanmoqda...</div>;

  const hasAudio = formData.item_type === "listening_question";
  const hasPassage = formData.item_type === "reading_question";

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <button
        onClick={() => router.push(`/exam/exams/${examId}/blocks/${blockId}`)}
        className="text-blue-600 mb-4 inline-block hover:underline"
      >
        ← Blockga qaytish
      </button>

      <h1 className="text-3xl font-bold mb-6">
        {itemId ? "Savolni tahrirlash" : "Yangi savol qo'shish"}
      </h1>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-5">
        {/* Item turi */}
        <div>
          <label className="block text-sm font-medium mb-1.5">Savol turi</label>
          <select
            name="item_type"
            value={formData.item_type}
            onChange={handleChange}
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
          >
            <option value="reading_question">📖 Reading Question</option>
            <option value="listening_question">🎧 Listening Question</option>
            <option value="writing_task">✍️ Writing Task</option>
            <option value="speaking_task">🎤 Speaking Task</option>
          </select>
        </div>

        {/* Title */}
        <div>
          <label className="block text-sm font-medium mb-1.5">
            Sarlavha <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            placeholder="Masalan: Question 1 - Main idea"
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
          />
        </div>

        {/* Audio upload (faqat Listening uchun) */}
        {hasAudio && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold mb-3 text-blue-900">🎧 Audio fayl</h3>
            <AudioUpload
              currentUrl={formData.audio_url}
              onUpload={handleAudioUploaded}
            />
          </div>
        )}

        {/* Passage (faqat Reading uchun) */}
        {hasPassage && (
          <div>
            <label className="block text-sm font-medium mb-1.5">
              📖 Passage (matn)
            </label>
            <textarea
              name="passage_text"
              value={formData.passage_text}
              onChange={handleChange}
              rows={6}
              placeholder="Reading uchun matn..."
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 font-mono text-sm"
            />
          </div>
        )}

        {/* Question text */}
        <div>
          <label className="block text-sm font-medium mb-1.5">
            Savol matni <span className="text-red-500">*</span>
          </label>
          <textarea
            name="question_text"
            value={formData.question_text}
            onChange={handleChange}
            required
            rows={2}
            placeholder="What is the main idea of the passage?"
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
          />
        </div>

        {/* Variantlar */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium">Variantlar</label>
            <button
              type="button"
              onClick={handleAddOption}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              + Variant qoshish
            </button>
          </div>

          <div className="space-y-2">
            {options.map((opt, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={opt.is_correct}
                  onChange={(e) => handleOptionChange(idx, "is_correct", e.target.checked)}
                  className="w-5 h-5 text-emerald-600 rounded"
                  title="To&rsquo;g&rsquo;ri javob"
                />
                <input
                  type="text"
                  value={opt.text}
                  onChange={(e) => handleOptionChange(idx, "text", e.target.value)}
                  placeholder={`Variant ${String.fromCharCode(65 + idx)}`}
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2"
                />
                <span
                  className={`text-xs font-semibold px-2 py-1 rounded ${
                    opt.is_correct ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"
                  }`}
                >
                  {String.fromCharCode(65 + idx)}
                </span>
                {options.length > 2 && (
                  <button
                    type="button"
                    onClick={() => handleRemoveOption(idx)}
                    className="text-red-500 hover:text-red-700 font-bold"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Order va Score */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">Tartib</label>
            <input
              type="number"
              name="order"
              value={formData.order}
              onChange={handleChange}
              min={1}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">Maks ball</label>
            <input
              type="number"
              name="max_score"
              value={formData.max_score}
              onChange={handleChange}
              min={0}
              step={0.5}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
            />
          </div>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg">❌ {error}</div>
        )}

        <div className="flex gap-3 pt-4 border-t">
          <button
            type="button"
            onClick={() => router.push(`/exam/exams/${examId}/blocks/${blockId}`)}
            className="px-6 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Bekor qilish
          </button>
          <button
            type="submit"
            disabled={saving}
            className="flex-1 bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold"
          >
            {saving ? "Saqlanmoqda..." : "💾 Saqlash"}
          </button>
        </div>
      </form>
    </div>
  );
}
