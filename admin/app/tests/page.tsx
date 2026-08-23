// admin/app/tests/page.tsx
'use client';

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { Plus, RefreshCw, FileQuestion, AlertCircle } from 'lucide-react';
import { Test, CefrLevel, CEFR_LEVELS } from '@/types/test';
import { testsApi, ApiError } from '@/lib/api_client';
import TestListTable from '@/components/tests/TestListTable';
import TestFormModal from '@/components/tests/TestFormModal';
import DeleteConfirmModal from '@/components/tests/DeleteConfirmModal';

export default function TestsPage() {
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
        <button
          onClick={handleOpenCreate}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
        >
          <Plus size={18} />
          Yangi test
        </button>
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
