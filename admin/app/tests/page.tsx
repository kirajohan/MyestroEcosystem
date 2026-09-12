// admin/app/tests/page.tsx
'use client';

import Link from "next/link";
import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { Plus, RefreshCw, FileQuestion, AlertCircle } from 'lucide-react';
import { Test, CefrLevel, CEFR_LEVELS } from '@/types/test';
import { testsApi, ApiError } from '@/lib/api_client';
import TestListTable from '@/components/tests/TestListTable';
import TestFormModal from '@/components/tests/TestFormModal';
import DeleteConfirmModal from '@/components/tests/DeleteConfirmModal';
import { Sparkles, Loader2 } from 'lucide-react';
import { AITestGenerateRequest } from '@/types/test';
import { useRouter } from "next/navigation";




export default function TestsPage() {
   const router = useRouter();
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [aiGenerating, setAiGenerating] = useState(false);
  const [aiForm, setAiForm] = useState({
    title: '',
    cefr_level: 'A1' as CefrLevel,
    num_questions: 5,
    topic: 'General English'
  });
  // ─── State ─────────────────────────────────────────────────
  const [tests, setTests] = useState<Test[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter
  const [filterLevel, setFilterLevel] = useState<string>('');

  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [editingTest, setEditingTest] = useState<Test | null>(null);
  const [deleteTestId, setDeleteTestId] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);

  // ─── Fetch Tests ───────────────────────────────────────────
  const fetchTests = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params: { level?: string; active_only?: boolean } = {};
      if (filterLevel) params.level = filterLevel;

      const data = await testsApi.list(params);
      setTests(data);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Testlarni yuklashda xatolik';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }, [filterLevel]);

  useEffect(() => {
    fetchTests();
  }, [fetchTests]);

  // ─── Handlers ──────────────────────────────────────────────
  const handleAiGenerate = async () => {
  if (!aiForm.title.trim()) {
    toast.error("Test sarlavhasini kiriting");
    return;
  }
  
  setAiGenerating(true);
  try {
    await testsApi.generateWithAI(aiForm as AITestGenerateRequest);
    toast.success("🤖 Test muvaffaqiyatli yaratildi!");
    setIsAiModalOpen(false);
    setAiForm({ title: '', cefr_level: 'A1', num_questions: 5, topic: 'General English' });
    fetchTests(); // Ro'yxatni yangilash
  } catch (err) {
    const message = err instanceof ApiError ? err.message : "AI test yaratishda xatolik";
    toast.error(message);
  } finally {
    setAiGenerating(false);
  }
};
  const handleOpenCreate = () => {
    setEditingTest(null);
    setIsFormModalOpen(true);
  };

  const handleOpenEdit = (test: Test) => {
    setEditingTest(test);
    setIsFormModalOpen(true);
  };

  const handleFormSuccess = () => {
    setIsFormModalOpen(false);
    setEditingTest(null);
    fetchTests();
  };

  const handleDelete = async () => {
    if (!deleteTestId) return;

    setDeleting(true);
    try {
      await testsApi.delete(deleteTestId);
      toast.success("✅ Test o'chirildi");
      setDeleteTestId(null);
      fetchTests();
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "O'chirishda xatolik";
      toast.error(message);
    } finally {
      setDeleting(false);
    }
  };

  // ─── Render ────────────────────────────────────────────────
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Testlar</h1>
          <p className="text-gray-600 mt-1">
            Telegram Quiz Poll uchun CEFR testlarini boshqarish
          </p>
        </div>
        <div className="flex gap-3">
          <Link
            href="/tests/import"
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-semibold flex items-center gap-2"
          >
            📥 Import (JSON)
          </Link>
          <Link
            href="/tests/new"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            + Yangi test
          </Link>
        </div>
      </div>
      {/* Filter Bar */}
      <div className="flex items-center gap-3 flex-wrap">
        <label className="text-sm text-gray-600 font-medium">CEFR daraja:</label>
        <select
          value={filterLevel}
          onChange={(e) => setFilterLevel(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
        >
          <option value="">Barchasi</option>
          {CEFR_LEVELS.map((level) => (
            <option key={level} value={level}>{level}</option>
          ))}
        </select>

        <button
          onClick={fetchTests}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Yangilash
        </button>

        {!loading && (
          <span className="text-sm text-gray-500 ml-auto">
            {tests.length} ta test topildi
          </span>
        )}
      </div>

      {/* Error State */}
      {error && (
        <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle size={20} className="text-red-500 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium text-red-800">Yuklashda xatolik</p>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
          <button
            onClick={fetchTests}
            className="text-sm text-red-600 hover:text-red-800 font-medium underline"
          >
            Qayta urinish
          </button>
        </div>
      )}

      {/* Content */}
      {loading ? (
        <LoadingSkeleton />
      ) : tests.length === 0 ? (
        <EmptyState onCreateClick={handleOpenCreate} />
      ) : (
        <TestListTable
          tests={tests}
          onEdit={handleOpenEdit}
          onDelete={(id) => setDeleteTestId(id)}
        />
      )}

      {/* Modals */}
      <TestFormModal
        isOpen={isFormModalOpen}
        onClose={() => {
          setIsFormModalOpen(false);
          setEditingTest(null);
        }}
        onSuccess={handleFormSuccess}
        editingTest={editingTest}
      />

      <DeleteConfirmModal
        isOpen={!!deleteTestId}
        onClose={() => setDeleteTestId(null)}
        onConfirm={handleDelete}
        loading={deleting}
        title="Testni &apos;chirish"
        description="Bu testni &apos;chirishni tasdiqlaysizmi? Barcha savollar ham &apos;chiriladi. Bu amal qaytarib bo&apos;lmaydi."
      />
      {/* AI Generate Modal */}
{isAiModalOpen && (
  <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
    <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden">
      <div className="p-6 border-b border-gray-100 bg-gradient-to-r from-purple-50 to-indigo-50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center text-purple-600">
            <Sparkles size={20} />
          </div>
          <div>
            <h2 className="text-lg font-bold text-gray-900">AI Test Generator</h2>
            <p className="text-sm text-gray-600">Bir necha soniyada toliq test yarating</p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Test sarlavhasi *</label>
          <input
            type="text"
            value={aiForm.title}
            onChange={(e) => setAiForm({ ...aiForm, title: e.target.value })}
            placeholder="Masalan: A1 Grammar Quiz"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">CEFR Daraja</label>
            <select
              value={aiForm.cefr_level}
              onChange={(e) => setAiForm({ ...aiForm, cefr_level: e.target.value as CefrLevel })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white"
            >
              {CEFR_LEVELS.map((level) => (
                <option key={level} value={level}>{level}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Savollar soni</label>
            <input
              type="number"
              min={3}
              max={20}
              value={aiForm.num_questions}
              onChange={(e) => setAiForm({ ...aiForm, num_questions: parseInt(e.target.value) || 5 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Mavzu (ixtiyoriy)</label>
          <input
            type="text"
            value={aiForm.topic}
            onChange={(e) => setAiForm({ ...aiForm, topic: e.target.value })}
            placeholder="Masalan: Present Simple, Food, Travel"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>
      </div>

      <div className="p-6 border-t border-gray-100 bg-gray-50 flex justify-end gap-3">
        <button
          onClick={() => setIsAiModalOpen(false)}
          disabled={aiGenerating}
          className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-200 rounded-lg transition-colors"
        >
          Bekor qilish
        </button>
        <button
          onClick={handleAiGenerate}
          disabled={aiGenerating || !aiForm.title.trim()}
          className="px-6 py-2 text-sm font-medium bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
        >
          {aiGenerating ? (
            <>
              <Loader2 className="animate-spin" size={16} />
              Yaratilmoqda...
            </>
          ) : (
            <>
              <Sparkles size={16} />
              Yaratish
            </>
          )}
        </button>
      </div>
    </div>
  </div>
)}
    </div>
  );
}

// ─── Loading Skeleton ──────────────────────────────────────────
function LoadingSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="p-4 border-b border-gray-100 bg-gray-50">
        <div className="h-4 bg-gray-200 rounded w-1/4 animate-pulse" />
      </div>
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="p-4 border-b border-gray-50 flex items-center gap-4">
          <div className="h-4 bg-gray-200 rounded flex-1 animate-pulse" />
          <div className="h-6 bg-gray-100 rounded-full w-12 animate-pulse" />
          <div className="h-4 bg-gray-100 rounded w-16 animate-pulse" />
          <div className="h-8 bg-gray-100 rounded w-20 animate-pulse" />
        </div>
      ))}
    </div>
  );
}

// ─── Empty State ───────────────────────────────────────────────
function EmptyState({ onCreateClick }: { onCreateClick: () => void }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-16 text-center">
      <FileQuestion className="w-16 h-16 mx-auto mb-4 text-gray-300" />
      <h3 className="text-lg font-semibold text-gray-900 mb-2">Testlar mavjud emas</h3>
      <p className="text-gray-500 mb-6 max-w-md mx-auto">
        Birinchi testni yaratish orqali boshlang. Testlar Telegram botda Quiz Poll sifatida ko&apos;rsatiladi.
      </p>
      <button
        onClick={onCreateClick}
        className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
      >
        <Plus size={18} />
        Yangi test yaratish
      </button>
    </div>
  );
}
