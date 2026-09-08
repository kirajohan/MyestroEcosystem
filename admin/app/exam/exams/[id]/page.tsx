"use client";

import { useEffect, useState, useCallback, FormEvent } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

interface Exam {
  id: number;
  code: string;
  title: string;
  description?: string;
  exam_type: string;
  cefr_level?: string;
  time_limit_sec: number;
  is_published: boolean;
}

interface Block {
  id: number;
  block_type: string;
  title: string;
  description?: string;
  instructions?: string;
  order: number;
  time_limit_sec: number;
}

const TYPE_LABELS: Record<string, string> = {
  full: "🎯 Full Exam",
  listening: "🎧 Listening",
  reading: "📖 Reading",
  writing: "✍️ Writing",
  speaking: "🎤 Speaking",
};

// ✅ Faqat skill turlari (full yo'q!)
const BLOCK_TYPES = [
  { value: "listening", label: "🎧 Listening", icon: "🎧" },
  { value: "reading", label: "📖 Reading", icon: "📖" },
  { value: "writing", label: "✍️ Writing", icon: "✍️" },
  { value: "speaking", label: "🎤 Speaking", icon: "🎤" },
];

export default function ExamDetailPage() {
  const router = useRouter();
  const params = useParams();
  const examId = Number(params.id);
  const { token } = useAuth();

  const [exam, setExam] = useState<Exam | null>(null);
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddBlock, setShowAddBlock] = useState(false);
  const [savingBlock, setSavingBlock] = useState(false);

  // Block yaratish formasi
  const [blockForm, setBlockForm] = useState({
    title: "",
    block_type: "listening",
    order: 1,
    time_limit_sec: 600,
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const headers = { Authorization: `Bearer ${token}` };

      const examRes = await fetch(`${API_URL}/api/v2/exam/admin/exams/${examId}`, { headers });
      if (examRes.ok) {
        setExam(await examRes.json());
      }

      const blocksRes = await fetch(`${API_URL}/api/v2/exam/admin/exams/${examId}/blocks`, { headers });
      if (blocksRes.ok) {
        setBlocks(await blocksRes.json());
      }
    } catch (err) {
      console.error("Yuklash xatosi:", err);
    } finally {
      setLoading(false);
    }
  }, [token, examId]);

  useEffect(() => {
    if (token) loadData();
  }, [token, loadData]);

  async function handleDeleteBlock(blockId: number) {
    if (!confirm("Bu block va uning barcha savollarini o'chirishni xohlaysizmi?")) return;

    try {
      const res = await fetch(`${API_URL}/api/v2/exam/admin/blocks/${blockId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setBlocks(blocks.filter((b) => b.id !== blockId));
      }
    } catch (err) {
      console.error("O'chirish xatosi:", err);
    }
  }

  function openAddBlockModal() {
    const nextOrder = blocks.length + 1;
    setBlockForm({
      title: "",
      block_type: "listening",
      order: nextOrder,
      time_limit_sec: Math.floor((exam?.time_limit_sec || 600) / (blocks.length + 1 || 4)),
    });
    setShowAddBlock(true);
  }

  async function handleAddBlock(e: FormEvent) {
    e.preventDefault();
    setSavingBlock(true);

    try {
      const res = await fetch(`${API_URL}/api/v2/exam/admin/exams/${examId}/blocks`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: blockForm.title || `Block ${blockForm.order}`,
          block_type: blockForm.block_type, // ✅ Endi faqat skill turi bo'ladi
          order: blockForm.order,
          time_limit_sec: blockForm.time_limit_sec,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `HTTP ${res.status}`);
      }

      await loadData();
      setShowAddBlock(false);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Block qo'shishda xato");
    } finally {
      setSavingBlock(false);
    }
  }

  if (loading) return <div className="p-6">Yuklanmoqda...</div>;
  if (!exam) return <div className="p-6">Exam topilmadi</div>;

  // Full Exam uchun maxsus ko'rinish
  const isFullExam = exam.exam_type === "full";

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <button onClick={() => router.push("/exam/exams")} className="text-blue-600 mb-4">
        ← Examlarga qaytish
      </button>

      {/* Exam header */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-2xl font-bold">{exam.title}</h1>
            <p className="text-gray-500 font-mono text-sm">{exam.code}</p>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-sm ${
              exam.is_published ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"
            }`}
          >
            {exam.is_published ? "Published" : "Draft"}
          </span>
        </div>
            
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-500">Turi</div>
            <div className="font-semibold">{TYPE_LABELS[exam.exam_type] || exam.exam_type}</div>
          </div>
          <div>
            <div className="text-gray-500">Daraja</div>
            <div className="font-semibold">{exam.cefr_level || "—"}</div>
          </div>
          <div>
            <div className="text-gray-500">Umumiy vaqt</div>
            <div className="font-semibold">{Math.floor(exam.time_limit_sec / 60)} daq</div>
          </div>
          <div>
            <div className="text-gray-500">Blocklar</div>
            <div className="font-semibold">{blocks.length} ta</div>
          </div>
        </div>

        {exam.description && <p className="mt-4 text-gray-600">{exam.description}</p>}

        {/* Full Exam uchun eslatma */}
        {isFullExam && (
          <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
            <p className="text-sm text-purple-800">
              💡 <strong>Full Exam:</strong> Har bir skill uchun alohida block yarating 
              (Listening → Reading → Writing → Speaking).
            </p>
          </div>
        )}
      </div>

      {/* Blocks */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Blocklar</h2>
          <button
            onClick={openAddBlockModal}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium"
          >
            + Block qoshish
          </button>
        </div>

        {blocks.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-3">📋</div>
            <p>Hali block qoshilmagan.</p>
            <p className="text-sm mt-1">Birinchi blockni qoshing va savollar yarating.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {blocks.map((block) => (
              <div key={block.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded">
                        #{block.order}
                      </span>
                      <span className="text-sm font-medium px-2 py-0.5 rounded bg-blue-50 text-blue-700">
                        {TYPE_LABELS[block.block_type] || block.block_type}
                      </span>
                    </div>
                    <h3 className="font-semibold text-lg">{block.title}</h3>
                    {block.description && (
                      <p className="text-sm text-gray-600 mt-1">{block.description}</p>
                    )}
                    <div className="text-xs text-gray-500 mt-2">
                      ⏱️ Vaqt: {Math.floor(block.time_limit_sec / 60)} daq
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => router.push(`/exam/exams/${examId}/blocks/${block.id}`)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium px-3 py-1 rounded border border-blue-200 hover:bg-blue-50"
                    >
                      ✏️ Tahrirlash
                    </button>
                    <button
                      onClick={() => handleDeleteBlock(block.id)}
                      className="text-red-600 hover:text-red-800 text-sm font-medium px-3 py-1 rounded border border-red-200 hover:bg-red-50"
                    >
                      🗑️ Ochirish
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ═══ ADD BLOCK MODAL ═══ */}
      {showAddBlock && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">📦 Yangi Block qoshish</h3>
              <button
                onClick={() => setShowAddBlock(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleAddBlock} className="space-y-4">
              {/* Block Type Selection */}
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700">
                  Block turi <span className="text-red-500">*</span>
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {BLOCK_TYPES.map((type) => (
                    <button
                      key={type.value}
                      type="button"
                      onClick={() => setBlockForm((prev) => ({ ...prev, block_type: type.value }))}
                      className={`p-3 rounded-lg border-2 transition-all text-center ${
                        blockForm.block_type === type.value
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <div className="text-2xl mb-1">{type.icon}</div>
                      <div className="text-sm font-medium text-gray-700">
                        {type.label.split(" ")[1]}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Title */}
              <div>
                <label className="block text-sm font-medium mb-1.5 text-gray-700">
                  Block nomi
                </label>
                <input
                  type="text"
                  value={blockForm.title}
                  onChange={(e) => setBlockForm((prev) => ({ ...prev, title: e.target.value }))}
                  placeholder={`${BLOCK_TYPES.find(t => t.value === blockForm.block_type)?.label} Section`}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {/* Order & Time */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5 text-gray-700">
                    Tartib raqami
                  </label>
                  <input
                    type="number"
                    value={blockForm.order}
                    onChange={(e) => setBlockForm((prev) => ({ ...prev, order: Number(e.target.value) }))}
                    min={1}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5 text-gray-700">
                    Vaqt (daqiqada)
                  </label>
                  <input
                    type="number"
                    value={Math.floor(blockForm.time_limit_sec / 60)}
                    onChange={(e) => setBlockForm((prev) => ({ ...prev, time_limit_sec: Number(e.target.value) * 60 }))}
                    min={1}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setShowAddBlock(false)}
                  className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium text-gray-700"
                >
                  Bekor qilish
                </button>
                <button
                  type="submit"
                  disabled={savingBlock}
                  className="flex-1 bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold"
                >
                  {savingBlock ? "Saqlanmoqda..." : "✅ Qo'shish"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}