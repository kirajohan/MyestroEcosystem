'use client';

import { useEffect, useState, useMemo } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { authFetch } from '@/lib/auth';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Plus,
  Trash2,
  Eye,
  Search,
  X,
  Clock,
  CheckCircle2,
  FileText,
  AlertCircle,
  Filter,
  ChevronRight,
  ClipboardCheck,
} from 'lucide-react';

interface Exam {
  id: number;
  code: string;
  title: string;
  description: string | null;
  exam_type: string;
  cefr_level: string | null;
  time_limit_sec: number;
  is_published: boolean;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://myestroeco-backend-production.up.railway.app';

const TYPE_ICONS: Record<string, string> = {
  full: '🎯',
  listening: '🎧',
  reading: '📖',
  writing: '✍️',
  speaking: '🎤',
};

const TYPE_LABELS: Record<string, string> = {
  full: 'Full Exam',
  listening: 'Listening',
  reading: 'Reading',
  writing: 'Writing',
  speaking: 'Speaking',
};

export default function ExamsListPage() {
  const router = useRouter();
  const { token } = useAuth();

  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [deleteId, setDeleteId] = useState<number | null>(null);

  useEffect(() => {
    async function loadExams() {
      setLoading(true);
      setError('');

      try {
        const res = await authFetch(`${API_URL}/api/v2/exam/admin/exams`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        setExams(data.items || []);
      } catch (err) {
        console.error('Examlar yuklanmadi:', err);
        setError('Examlar yuklanmadi. Backendni tekshiring.');
      } finally {
        setLoading(false);
      }
    }

    if (token) loadExams();
  }, [token]);

  const filteredExams = useMemo(() => {
    let result = exams;

    if (filterType !== 'all') {
      result = result.filter((e) => e.exam_type === filterType);
    }

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (e) =>
          e.title.toLowerCase().includes(q) ||
          e.code.toLowerCase().includes(q) ||
          (e.description || '').toLowerCase().includes(q)
      );
    }

    return result;
  }, [exams, filterType, searchQuery]);

  async function handleDelete(examId: number) {
    try {
      const res = await authFetch(`${API_URL}/api/v2/exam/admin/exams/${examId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        setExams((prev) => prev.filter((e) => e.id !== examId));
      }
    } catch (err) {
      console.error('Ochirish xatosi:', err);
    } finally {
      setDeleteId(null);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Examlar</h1>
          <p className="text-sm md:text-base text-slate-600 mt-1">
            Jami: {exams.length} ta imtihon
          </p>
        </div>
        <Link
          href="/exam/create"
          className="flex items-center justify-center gap-2 px-5 py-2.5 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl font-medium text-sm hover:from-orange-600 hover:to-orange-700 transition-all shadow-lg shadow-orange-500/20"
        >
          <Plus className="w-4 h-4" />
          Yangi Exam
        </Link>
      </div>

      {/* Search + Filter */}
      <div className="bg-white rounded-xl md:rounded-2xl border border-slate-200 p-4 shadow-sm">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Exam nomi yoki kodi boyicha qidirish..."
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

          <div className="flex gap-1.5 bg-slate-100 p-1 rounded-xl overflow-x-auto">
            <button
              onClick={() => setFilterType('all')}
              className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                filterType === 'all'
                  ? 'bg-white text-orange-600 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Barchasi
            </button>
            {Object.entries(TYPE_LABELS).map(([key, label]) => (
              <button
                key={key}
                onClick={() => setFilterType(key)}
                className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  filterType === key
                    ? 'bg-white text-orange-600 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {TYPE_ICONS[key]} {label}
              </button>
            ))}
          </div>
        </div>
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
            <p className="text-sm text-red-700">{error}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Content */}
      {loading ? (
        <LoadingSkeleton />
      ) : filteredExams.length === 0 ? (
        <EmptyState hasFilters={!!(searchQuery || filterType !== 'all')} />
      ) : (
        <>
          {/* Desktop Table */}
          <div className="hidden md:block bg-white rounded-2xl border border-slate-200 shadow-sm overflow-x-auto">
            <table className="w-full min-w-[720px]">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Turi
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Nomi
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Kod
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Daraja
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Vaqt
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Amallar
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredExams.map((exam, index) => (
                  <motion.tr
                    key={exam.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.03 }}
                    className="hover:bg-slate-50/50 transition-colors"
                  >
                    <td className="px-6 py-4 text-xl">{TYPE_ICONS[exam.exam_type] || '📝'}</td>
                    <td className="px-6 py-4">
                      <p className="font-semibold text-slate-900">{exam.title}</p>
                      {exam.description && (
                        <p className="text-xs text-slate-500 mt-0.5 truncate max-w-xs">
                          {exam.description}
                        </p>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm font-mono text-slate-600">{exam.code}</td>
                    <td className="px-6 py-4">
                      {exam.cefr_level ? (
                        <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
                          {exam.cefr_level}
                        </span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-600">
                      <span className="inline-flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        {Math.floor(exam.time_limit_sec / 60)} daq
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {exam.is_published ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3" />
                          Published
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">
                          Draft
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => router.push(`/exam/exams/${exam.id}`)}
                          className="p-2 text-slate-500 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                          title="Korish"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setDeleteId(exam.id)}
                          className="p-2 text-slate-500 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                          title="Ochirish"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile Cards */}
          <div className="md:hidden space-y-3">
            {filteredExams.map((exam, index) => (
              <motion.div
                key={exam.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4"
              >
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="w-12 h-12 bg-gradient-to-br from-orange-400 to-orange-600 rounded-xl flex items-center justify-center text-2xl shadow-sm">
                      {TYPE_ICONS[exam.exam_type] || '📝'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-slate-900 truncate">{exam.title}</h3>
                      <p className="text-xs text-slate-500 font-mono mt-0.5">{exam.code}</p>
                    </div>
                  </div>
                  {exam.is_published ? (
                    <span className="flex-shrink-0 px-2 py-1 rounded-lg text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      Published
                    </span>
                  ) : (
                    <span className="flex-shrink-0 px-2 py-1 rounded-lg text-[10px] font-bold bg-slate-100 text-slate-600 border border-slate-200">
                      Draft
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-2 mb-3">
                  {exam.cefr_level && (
                    <div className="p-2 bg-blue-50 rounded-lg text-center">
                      <p className="text-xs text-slate-500">CEFR</p>
                      <p className="text-sm font-bold text-blue-700">{exam.cefr_level}</p>
                    </div>
                  )}
                  <div className="p-2 bg-slate-50 rounded-lg text-center">
                    <p className="text-xs text-slate-500">Vaqt</p>
                    <p className="text-sm font-bold text-slate-900">
                      {Math.floor(exam.time_limit_sec / 60)} daq
                    </p>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg text-center">
                    <p className="text-xs text-slate-500">Turi</p>
                    <p className="text-sm font-bold text-slate-900">
                      {TYPE_LABELS[exam.exam_type] || 'Exam'}
                    </p>
                  </div>
                </div>

                <div className="flex gap-2 pt-3 border-t border-slate-100">
                  <button
                    onClick={() => router.push(`/exam/exams/${exam.id}`)}
                    className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-orange-50 text-orange-700 rounded-lg font-medium text-xs hover:bg-orange-100 transition-colors"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    Korish
                  </button>
                  <button
                    onClick={() => setDeleteId(exam.id)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </>
      )}

      {/* Delete Confirm */}
      <AnimatePresence>
        {deleteId !== null && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setDeleteId(null)}
              className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-x-4 top-[10%] max-h-[85vh] overflow-y-auto md:inset-auto md:left-1/2 md:top-[25%] md:-translate-x-1/2 w-full md:max-w-md bg-white rounded-2xl shadow-2xl border border-slate-200 z-50"
            >
              <div className="p-5 border-b border-slate-100">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-red-100 rounded-xl flex items-center justify-center">
                    <AlertCircle className="w-5 h-5 text-red-600" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900">Examni ochirish</h3>
                </div>
              </div>
              <div className="p-5">
                <p className="text-sm text-slate-600">
                  Bu examni va uning barcha blocklarini ochirishni tasdiqlaysizmi? Bu amal qaytarib bolmaydi.
                </p>
              </div>
              <div className="p-4 border-t border-slate-100 bg-slate-50 flex gap-2">
                <button
                  onClick={() => setDeleteId(null)}
                  className="flex-1 px-4 py-2.5 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-100 transition"
                >
                  Bekor qilish
                </button>
                <button
                  onClick={() => handleDelete(deleteId)}
                  className="flex-1 px-4 py-2.5 text-sm font-medium bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl hover:from-red-600 hover:to-red-700 transition-all"
                >
                  Ochirish
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="p-4 border-b border-slate-100 bg-slate-50">
        <div className="h-4 bg-slate-200 rounded w-1/4 animate-pulse" />
      </div>
      {[1, 2, 3].map((i) => (
        <div key={i} className="p-4 border-b border-slate-50 flex items-center gap-4">
          <div className="w-12 h-12 bg-slate-200 rounded-xl animate-pulse" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-slate-200 rounded w-3/4 animate-pulse" />
            <div className="h-3 bg-slate-100 rounded w-1/2 animate-pulse" />
          </div>
        </div>
      ))}
    </div>
  );
}

function EmptyState({ hasFilters }: { hasFilters: boolean }) {
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-sm">
      <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
        <ClipboardCheck className="w-8 h-8 text-slate-300" />
      </div>
      <h3 className="text-lg font-semibold text-slate-900 mb-1">
        {hasFilters ? 'Exam topilmadi' : 'Hali exam yaratilmagan'}
      </h3>
      <p className="text-sm text-slate-500 mb-6 max-w-md mx-auto">
        {hasFilters
          ? 'Filter yoki qidiruv shartlariga mos exam topilmadi'
          : 'Birinchi examni yaratish orqali boshlang'}
      </p>
      {!hasFilters && (
        <Link
          href="/exam/create"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-orange-500 to-orange-600 text-white font-medium rounded-xl hover:from-orange-600 hover:to-orange-700 transition-all shadow-lg shadow-orange-500/20"
        >
          <Plus className="w-4 h-4" />
          Birinchi examni yarating
        </Link>
      )}
    </div>
  );
}