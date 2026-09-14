'use client';

import Link from 'next/link';
import { useState, useEffect, useCallback, useMemo } from 'react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  RefreshCw,
  FileQuestion,
  AlertCircle,
  X,
  Search,
  ClipboardCheck,
  CheckCircle2,
  Archive,
  Upload,
} from 'lucide-react';
import { Test, CefrLevel, CEFR_LEVELS } from '@/types/test';
import { testsApi, ApiError } from '@/lib/api_client';
import TestListTable from '@/components/tests/TestListTable';
import TestFormModal from '@/components/tests/TestFormModal';
import DeleteConfirmModal from '@/components/tests/DeleteConfirmModal';

export default function TestsPage() {
  const [tests, setTests] = useState<Test[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [filterLevel, setFilterLevel] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');

  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [editingTest, setEditingTest] = useState<Test | null>(null);
  const [deleteTestId, setDeleteTestId] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);

  const stats = useMemo(() => {
    return {
      total: tests.length,
      active: tests.filter((t) => t.is_active).length,
      draft: tests.filter((t) => !t.is_active).length,
    };
  }, [tests]);

  const filteredTests = useMemo(() => {
    let result = tests;

    if (filterLevel) {
      result = result.filter((t) => t.cefr_level === filterLevel);
    }

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (t) =>
          t.title?.toLowerCase().includes(q) ||
          t.description?.toLowerCase().includes(q)
      );
    }

    return result;
  }, [tests, filterLevel, searchQuery]);

  const fetchTests = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await testsApi.list({});
      setTests(data);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Testlarni yuklashda xatolik';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTests();
  }, [fetchTests]);

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
      toast.success('Test ochirildi');
      setDeleteTestId(null);
      fetchTests();
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Ochirishda xatolik';
      toast.error(message);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Testlar</h1>
            <p className="text-sm md:text-base text-slate-600 mt-1">
              Telegram Quiz Poll uchun CEFR testlarini boshqaring
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-2">
          <Link
            href="/tests/import"
            className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-xl hover:bg-slate-50 transition-all font-medium text-sm shadow-sm"
          >
            <Upload className="w-4 h-4" />
            <span className="hidden sm:inline">Import (JSON)</span>
            <span className="sm:hidden">Import</span>
          </Link>
          <Link
            href="/tests/new"
            className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl hover:from-orange-600 hover:to-orange-700 transition-all font-medium text-sm shadow-lg shadow-orange-500/20"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Yangi test</span>
            <span className="sm:hidden">Yangi</span>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl md:rounded-2xl border border-slate-200 p-4 md:p-5 shadow-sm"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="w-9 h-9 md:w-10 md:h-10 bg-slate-100 rounded-lg flex items-center justify-center">
              <ClipboardCheck className="w-4 h-4 md:w-5 md:h-5 text-slate-600" />
            </div>
          </div>
          <p className="text-xl md:text-2xl font-bold text-slate-900">{stats.total}</p>
          <p className="text-xs text-slate-500 mt-1">Jami testlar</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="bg-white rounded-xl md:rounded-2xl border border-emerald-100 p-4 md:p-5 shadow-sm"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="w-9 h-9 md:w-10 md:h-10 bg-emerald-50 rounded-lg flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4 md:w-5 md:h-5 text-emerald-600" />
            </div>
          </div>
          <p className="text-xl md:text-2xl font-bold text-slate-900">{stats.active}</p>
          <p className="text-xs text-slate-500 mt-1">Faol testlar</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl md:rounded-2xl border border-orange-100 p-4 md:p-5 shadow-sm col-span-2 lg:col-span-1"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="w-9 h-9 md:w-10 md:h-10 bg-orange-50 rounded-lg flex items-center justify-center">
              <Archive className="w-4 h-4 md:w-5 md:h-5 text-orange-600" />
            </div>
          </div>
          <p className="text-xl md:text-2xl font-bold text-slate-900">{stats.draft}</p>
          <p className="text-xs text-slate-500 mt-1">Qoralama</p>
        </motion.div>
      </div>

      {/* Search + Filter Bar */}
      <div className="bg-white rounded-xl md:rounded-2xl border border-slate-200 p-4 shadow-sm">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Test nomi boyicha qidirish..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          <div className="flex gap-2">
            <div className="flex items-center gap-2 bg-slate-100 rounded-xl p-1 overflow-x-auto">
              <button
                onClick={() => setFilterLevel('')}
                className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  filterLevel === ''
                    ? 'bg-white text-orange-600 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Barchasi
              </button>
              {CEFR_LEVELS.map((level) => (
                <button
                  key={level}
                  onClick={() => setFilterLevel(level)}
                  className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    filterLevel === level
                      ? 'bg-white text-orange-600 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>

            <button
              onClick={fetchTests}
              disabled={loading}
              className="flex-shrink-0 p-2.5 text-slate-600 hover:bg-slate-100 rounded-xl transition disabled:opacity-50"
              title="Yangilash"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {(searchQuery || filterLevel) && (
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between">
            <p className="text-xs md:text-sm text-slate-600">
              Topildi:{' '}
              <span className="font-semibold text-slate-900">{filteredTests.length}</span> ta test
            </p>
            <button
              onClick={() => {
                setSearchQuery('');
                setFilterLevel('');
              }}
              className="text-xs md:text-sm text-orange-600 hover:text-orange-700 font-medium"
            >
              Tozalash
            </button>
          </div>
        )}
      </div>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-xl"
          >
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-red-800">Yuklashda xatolik</p>
              <p className="text-sm text-red-600 mt-1">{error}</p>
            </div>
            <button
              onClick={fetchTests}
              className="text-sm text-red-600 hover:text-red-800 font-medium"
            >
              Qayta urinish
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Content */}
      {loading ? (
        <LoadingSkeleton />
      ) : filteredTests.length === 0 ? (
        <EmptyState
          onCreateClick={handleOpenCreate}
          hasFilters={!!(searchQuery || filterLevel)}
        />
      ) : (
        <div className="bg-white rounded-xl md:rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <TestListTable
            tests={filteredTests}
            onEdit={handleOpenEdit}
            onDelete={(id) => setDeleteTestId(id)}
          />
        </div>
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
        title="Testni ochirish"
        description="Bu testni ochirishni tasdiqlaysizmi? Barcha savollar ham ochiriladi."
      />
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="bg-white rounded-xl md:rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
      <div className="p-4 border-b border-slate-100 bg-slate-50">
        <div className="h-4 bg-slate-200 rounded w-1/4 animate-pulse" />
      </div>
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="p-4 border-b border-slate-50 flex items-center gap-4">
          <div className="h-4 bg-slate-200 rounded flex-1 animate-pulse" />
          <div className="h-6 bg-slate-100 rounded-full w-12 animate-pulse" />
          <div className="h-4 bg-slate-100 rounded w-16 animate-pulse hidden sm:block" />
          <div className="h-8 bg-slate-100 rounded w-20 animate-pulse" />
        </div>
      ))}
    </div>
  );
}

function EmptyState({
  onCreateClick,
  hasFilters,
}: {
  onCreateClick: () => void;
  hasFilters: boolean;
}) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-8 md:p-16 text-center shadow-sm">
      <div className="w-16 h-16 md:w-20 md:h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
        <FileQuestion className="w-8 h-8 md:w-10 md:h-10 text-slate-300" />
      </div>
      <h3 className="text-lg font-semibold text-slate-900 mb-2">
        {hasFilters ? 'Testlar topilmadi' : 'Testlar mavjud emas'}
      </h3>
      <p className="text-sm text-slate-500 mb-6 max-w-md mx-auto">
        {hasFilters
          ? 'Filter yoki qidiruv shartlariga mos test topilmadi'
          : 'Birinchi testni yaratish orqali boshlang'}
      </p>
      {!hasFilters && (
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={onCreateClick}
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-gradient-to-r from-orange-500 to-orange-600 text-white font-medium rounded-xl hover:from-orange-600 hover:to-orange-700 transition-all shadow-lg shadow-orange-500/20"
          >
            <Plus className="w-4 h-4" />
            Yangi test yaratish
          </button>
          <Link
            href="/tests/import"
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-white border border-slate-200 text-slate-700 font-medium rounded-xl hover:bg-slate-50 transition-all"
          >
            <Upload className="w-4 h-4" />
            Import qilish
          </Link>
        </div>
      )}
    </div>
  );
}