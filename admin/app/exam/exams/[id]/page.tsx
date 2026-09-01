"use client";

import { useEffect, useState, useCallback } from "react";
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

export default function ExamDetailPage() {
  const router = useRouter();
  const params = useParams();
  const examId = Number(params.id);
  const { token } = useAuth();

  const [exam, setExam] = useState<Exam | null>(null);
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddBlock, setShowAddBlock] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const headers = { Authorization: `Bearer ${token}` };

      // Exam ma'lumotlari
      const examRes = await fetch(`${API_URL}/api/v2/exam/admin/exams/${examId}`, { headers });
      if (examRes.ok) {
        setExam(await examRes.json());
      }

      // Blocklar
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
    if (!confirm("Bu block va uning barcha savollarini ochirishni xohlaysizmi?")) return;

    try {
      const res = await fetch(`${API_URL}/api/v2/exam/admin/blocks/${blockId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setBlocks(blocks.filter((b) => b.id !== blockId));
      }
    } catch (err) {
      console.error("Ochirish xatosi:", err);
    }
  }

  async function handleAddBlock() {
    const nextOrder = blocks.length + 1;
    try {
      const res = await fetch(`${API_URL}/api/v2/exam/admin/exams/${examId}/blocks`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: `Block ${nextOrder}`,
          block_type: exam?.exam_type,
          order: nextOrder,
          time_limit_sec: Math.floor((exam?.time_limit_sec || 600) / 3),
        }),
      });
      if (res.ok) {
        await loadData();
        setShowAddBlock(false);
      }
    } catch (err) {
      console.error("Qo'shish xatosi:", err);
    }
  }

  if (loading) return <div className="p-6">Yuklanmoqda...</div>;
  if (!exam) return <div className="p-6">Exam topilmadi</div>;

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
            <div className="text-gray-500">Vaqt</div>
            <div className="font-semibold">{Math.floor(exam.time_limit_sec / 60)} daq</div>
          </div>
          <div>
            <div className="text-gray-500">Blocklar</div>
            <div className="font-semibold">{blocks.length} ta</div>
          </div>
        </div>

        {exam.description && <p className="mt-4 text-gray-600">{exam.description}</p>}
      </div>

      {/* Blocks */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Blocklar</h2>
          <button
            onClick={handleAddBlock}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            + Block qoshish
          </button>
        </div>

        {blocks.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            Hali block qoshilmagan. Birinchi blockni qo&rsquo;shing.
          </div>
        ) : (
          <div className="space-y-3">
            {blocks.map((block) => (
              <div key={block.id} className="border rounded-lg p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded">
                        #{block.order}
                      </span>
                      <span className="text-sm text-gray-500">
                        {TYPE_LABELS[block.block_type] || block.block_type}
                      </span>
                    </div>
                    <h3 className="font-semibold">{block.title}</h3>
                    {block.description && (
                      <p className="text-sm text-gray-600 mt-1">{block.description}</p>
                    )}
                    <div className="text-xs text-gray-500 mt-2">
                      Vaqt: {Math.floor(block.time_limit_sec / 60)} daq
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => router.push(`/exam/exams/${examId}/blocks/${block.id}`)}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Tahrirlash
                    </button>
                    <button
                      onClick={() => handleDeleteBlock(block.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Ochirish
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}