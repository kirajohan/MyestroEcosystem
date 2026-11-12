'use client';

import { useEffect, useState, useCallback, FormEvent } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft,
  Plus,
  Trash2,
  Pencil,
  Clock,
  CheckCircle2,
  FileText,
  X,
  Headphones,
  BookOpen,
  PenTool,
  Mic,
  AlertCircle,
  Eye,
  EyeOff,
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://myestroeco-backend-production.up.railway.app';

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
  order: number;
  time_limit_sec: number;
}

const BLOCK_TYPES = [
  { value: 'listening', label: 'Listening', icon: Headphones, color: 'blue' },
  { value: 'reading', label: 'Reading', icon: BookOpen, color: 'emerald' },
  { value: 'writing', label: 'Writing', icon: PenTool, color: 'purple' },
  { value: 'speaking', label: 'Speaking', icon: Mic, color: 'rose' },
];

export default function ExamDetailPage() {
  const router = useRouter();
  const params = useParams();
  const examId = Number(params.id);
  const { token } = useAuth();

  const [exam, setExam] = useState<Exam | null>(null);
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [loading, setLoading] = useState(true);
  
  // YANGI: Publish holatini o'zgartirish paytidagi loading holati
  const [updatingPublish, setUpdatingPublish] = useState(false);

  const [showAddBlock, setShowAddBlock] = useState(false);
  const [savingBlock, setSavingBlock] = useState(false);
  const [deleteBlockId, setDeleteBlockId] = useState<number | null>(null);

  const [blockForm, setBlockForm] = useState({
    title: '',
    block_type: 'listening',
    order: 1,
    time_limit_sec: 600,
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const headers = { Authorization: `Bearer ${token}` };

      const examRes = await fetch(`${API_URL}/api/v2/exam/admin/exams/${examId}`, { headers });
      if (examRes.ok) setExam(await examRes.json());

      const blocksRes = await fetch(`${API_URL}/api/v2/exam/admin/exams/${examId}/blocks`, {
        headers,
      });
      if (blocksRes.ok) setBlocks(await blocksRes.json());
    } catch (err) {
      console.error('Yuklash xatosi:', err);
    } finally {
      setLoading(false);
    }
  }, [token, examId]);

  useEffect(() => {
    if (token) loadData();
  }, [token, loadData]);

  // YANGI: Publish holatini o'zgartirish funksiyasi
  const handleTogglePublish = async () => {
    if (!exam) return;
    setUpdatingPublish(true);
    try {
      const res = await fetch(`${API_URL}/api/v2/exam/admin/exams/${examId}/publish`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ is_published: !exam.is_published }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      
      const data = await res.json();
      // [FE-01.1] Server state'ni to'g'ridan-to'g'ri yangilash (optimistik yangilash)
      setExam((prev) => prev ? { ...prev, is_published: data.is_published } : null);
    } catch (err) {
      console.error('Publish statusini o\'zgartirishda xato:', err);
      // [FE-04.2] Foydalanuvchiga aniq xato xabari
      alert('Holatni o\'zgartirishda xatolik yuz berdi. Qaytadan urinib ko\'ring.');
    } finally {
      setUpdatingPublish(false);
    }
  };

  function openAddBlockModal() {
    const nextOrder = blocks.length + 1;
    setBlockForm({
      title: '',
      block_type: 'listening',
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
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: blockForm.title || `Block ${blockForm.order}`,
          block_type: blockForm.block_type,
          order: blockForm.order,
          time_limit_sec: blockForm.time_limit_sec,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      await loadData();
      setShowAddBlock(false);
    } catch (err) {
      console.error('Block qoshishda xato:', err);
    } finally {
      setSavingBlock(false);
    }
  }

  async function handleDeleteBlock() {
    if (!deleteBlockId) return;
    try {
      const res = await fetch(`${API_URL}/api/v2/exam/admin/blocks/${deleteBlockId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setBlocks((prev) => prev.filter((b) => b.id !== deleteBlockId));
    } catch (err) {
      console.error('Ochirish xatosi:', err);
    } finally {
      setDeleteBlockId(null);
    }
  }

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[50vh]">
        <div className="w-8 h-8 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin" />
      </div>
    );
  }

  if (!exam) {
    return (
      <div className="p-6 flex flex-col items-center justify-center min-h-[50vh]">
        <AlertCircle className="w-12 h-12 text-red-400 mb-3" />
        <p className="text-slate-600">Exam topilmadi</p>
      </div>
    );
  }

  const getBlockTypeInfo = (type: string) =>
    BLOCK_TYPES.find((b) => b.value === type) || BLOCK_TYPES[0];

  return (
    <div className="space-y-6">
      {/* Back button */}
      <button
        onClick={() => router.push('/exam/exams')}
        className="flex items-center gap-2 text-sm text-slate-600 hover:text-orange-600 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Examlarga qaytish
      </button>

      {/* Exam Header */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
      >
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-5">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0 break-words">
              <h1 className="text-xl md:text-2xl font-bold text-white">{exam.title}</h1>
              <p className="text-sm text-white/80 font-mono mt-1">{exam.code}</p>
            </div>
            
            {/* O'ZGARTIRILDI: Interaktiv Publish/Draft tugmasi */}
            <button
              onClick={handleTogglePublish}
              disabled={updatingPublish}
              className={`flex-shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all border ${
                exam.is_published
                  ? 'bg-emerald-500/20 text-emerald-100 border-emerald-400/30 hover:bg-emerald-500/30'
                  : 'bg-white/10 text-white border-white/20 hover:bg-white/20'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              title={exam.is_published ? "Draft holatiga o'tkazish" : "Publish qilish"}
            >
              {updatingPublish ? (
                <div className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
              ) : exam.is_published ? (
                <EyeOff className="w-3.5 h-3.5" />
              ) : (
                <Eye className="w-3.5 h-3.5" />
              )}
              {exam.is_published ? 'Published' : 'Draft'}
            </button>
          </div>
        </div>

        <div className="p-5 grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="p-3 bg-slate-50 rounded-xl">
            <p className="text-xs text-slate-500 mb-1">Turi</p>
            <p className="text-sm font-semibold text-slate-900">{exam.exam_type}</p>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl">
            <p className="text-xs text-slate-500 mb-1">Daraja</p>
            <p className="text-sm font-semibold text-slate-900">{exam.cefr_level || '—'}</p>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl">
            <p className="text-xs text-slate-500 mb-1">Umumiy vaqt</p>
            <p className="text-sm font-semibold text-slate-900 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {Math.floor(exam.time_limit_sec / 60)} daq
            </p>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl">
            <p className="text-xs text-slate-500 mb-1">Blocklar</p>
            <p className="text-sm font-semibold text-slate-900">{blocks.length} ta</p>
          </div>
        </div>

        {exam.description && (
          <div className="px-5 pb-5">
            <p className="text-sm text-slate-600 bg-slate-50 p-3 rounded-xl">{exam.description}</p>
          </div>
        )}
      </motion.div>

      {/* Blocks Section */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <FileText className="w-5 h-5 text-orange-500" />
            Blocklar
          </h2>
          <button
            onClick={openAddBlockModal}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl font-medium text-sm hover:from-orange-600 hover:to-orange-700 transition-all shadow-lg shadow-orange-500/20"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Block qoshish</span>
            <span className="sm:hidden">Qoshish</span>
          </button>
        </div>

        {blocks.length === 0 ? (
          <div className="p-12 text-center">
            <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-slate-300" />
            </div>
            <h3 className="text-base font-semibold text-slate-900 mb-1">Hali block qoshilmagan</h3>
            <p className="text-sm text-slate-500 mb-4">
              Birinchi blockni qoshing va savollar yarating
            </p>
            <button
              onClick={openAddBlockModal}
              className="inline-flex items-center gap-2 px-4 py-2 bg-orange-50 text-orange-700 rounded-xl font-medium text-sm hover:bg-orange-100 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Block qoshish
            </button>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {blocks.map((block, index) => {
              const typeInfo = getBlockTypeInfo(block.block_type);
              const Icon = typeInfo.icon;

              return (
                <motion.div
                  key={block.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-4 hover:bg-slate-50/50 transition-colors group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-orange-100 to-orange-50 rounded-xl flex items-center justify-center flex-shrink-0 border border-orange-100">
                      <Icon className="w-6 h-6 text-orange-600" />
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-600">
                          #{block.order}
                        </span>
                        <span className="text-xs font-semibold text-orange-600">
                          {typeInfo.label}
                        </span>
                      </div>
                      <h3 className="font-semibold text-slate-900 truncate">{block.title}</h3>
                      {block.description && (
                        <p className="text-xs text-slate-500 mt-0.5 truncate">
                          {block.description}
                        </p>
                      )}
                      <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {Math.floor(block.time_limit_sec / 60)} daqiqa
                      </p>
                    </div>

                    <div className="flex items-center gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => router.push(`/exam/exams/${examId}/blocks/${block.id}`)}
                        className="p-2 text-slate-500 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                        title="Tahrirlash"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setDeleteBlockId(block.id)}
                        className="p-2 text-slate-500 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                        title="Ochirish"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      <div className="w-4 h-4 text-slate-400" />
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>

      {/* Add Block Modal */}
      <AnimatePresence>
        {showAddBlock && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowAddBlock(false)}
              className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed inset-x-4 top-[10%] md:inset-auto md:left-1/2 md:top-[15%] md:-translate-x-1/2 w-full md:max-w-md bg-white rounded-2xl shadow-2xl border border-slate-200 z-50 overflow-hidden max-h-[85vh] flex flex-col"
            >
              <div className="p-5 border-b border-slate-100 bg-gradient-to-r from-orange-500 to-orange-600 flex-shrink-0">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                    <Plus className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0 break-words">
                    <h2 className="text-lg font-bold text-white">Yangi Block qoshish</h2>
                    <p className="text-xs text-white/80">Skill turini tanlang</p>
                  </div>
                  <button
                    onClick={() => setShowAddBlock(false)}
                    className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <form onSubmit={handleAddBlock} className="p-5 space-y-5 overflow-y-auto flex-1">
                <div>
                  <label className="block text-sm font-semibold text-slate-900 mb-2">
                    Block turi <span className="text-red-500">*</span>
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {BLOCK_TYPES.map((type) => {
                      const Icon = type.icon;
                      const isSelected = blockForm.block_type === type.value;
                      return (
                        <button
                          key={type.value}
                          type="button"
                          onClick={() =>
                            setBlockForm((prev) => ({ ...prev, block_type: type.value }))
                          }
                          className={`p-4 rounded-xl border-2 transition-all ${
                            isSelected
                              ? 'border-orange-500 bg-orange-50'
                              : 'border-slate-200 hover:border-slate-300'
                          }`}
                        >
                          <Icon
                            className={`w-6 h-6 mx-auto mb-2 ${
                              isSelected ? 'text-orange-600' : 'text-slate-400'
                            }`}
                          />
                          <p
                            className={`text-sm font-medium ${
                              isSelected ? 'text-orange-700' : 'text-slate-600'
                            }`}
                          >
                            {type.label}
                          </p>
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                    Block nomi
                  </label>
                  <input
                    type="text"
                    value={blockForm.title}
                    onChange={(e) => setBlockForm((prev) => ({ ...prev, title: e.target.value }))}
                    placeholder={`${getBlockTypeInfo(blockForm.block_type).label} Section`}
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                      Tartib
                    </label>
                    <input
                      type="number"
                      value={blockForm.order}
                      onChange={(e) =>
                        setBlockForm((prev) => ({ ...prev, order: Number(e.target.value) }))
                      }
                      min={1}
                      className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                      Vaqt (daqiqada)
                    </label>
                    <input
                      type="number"
                      value={Math.floor(blockForm.time_limit_sec / 60)}
                      onChange={(e) =>
                        setBlockForm((prev) => ({
                          ...prev,
                          time_limit_sec: Number(e.target.value) * 60,
                        }))
                      }
                      min={1}
                      className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                    />
                  </div>
                </div>

                <div className="flex gap-2 pt-4 border-t border-slate-100">
                  <button
                    type="button"
                    onClick={() => setShowAddBlock(false)}
                    className="flex-1 px-4 py-2.5 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-100 transition"
                  >
                    Bekor qilish
                  </button>
                  <button
                    type="submit"
                    disabled={savingBlock}
                    className="flex-1 px-4 py-2.5 text-sm font-medium bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl hover:from-orange-600 hover:to-orange-700 disabled:opacity-50 transition-all shadow-lg shadow-orange-500/20"
                  >
                    {savingBlock ? 'Saqlanmoqda...' : 'Qoshish'}
                  </button>
                </div>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Delete Block Confirm */}
      <AnimatePresence>
        {deleteBlockId !== null && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setDeleteBlockId(null)}
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
                  <h3 className="text-lg font-bold text-slate-900">Blockni ochirish</h3>
                </div>
              </div>
              <div className="p-5">
                <p className="text-sm text-slate-600">
                  Bu block va uning barcha savollarini ochirishni tasdiqlaysizmi? Bu amal qaytarib bolmaydi.
                </p>
              </div>
              <div className="p-4 border-t border-slate-100 bg-slate-50 flex gap-2">
                <button
                  onClick={() => setDeleteBlockId(null)}
                  className="flex-1 px-4 py-2.5 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-100 transition"
                >
                  Bekor qilish
                </button>
                <button
                  onClick={handleDeleteBlock}
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