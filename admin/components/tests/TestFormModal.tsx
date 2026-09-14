'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import { X, FileText, CheckCircle } from 'lucide-react';
import {
  Test,
  TestCreate,
  TestUpdate,
  CefrLevel,
  CEFR_LEVELS,
  TestFormState,
  DEFAULT_TEST_FORM,
} from '@/types/test';
import { testsApi, ApiError } from '@/lib/api_client';

interface TestFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  editingTest: Test | null;
}

export default function TestFormModal({
  isOpen,
  onClose,
  onSuccess,
  editingTest,
}: TestFormModalProps) {
  const [form, setForm] = useState<TestFormState>(DEFAULT_TEST_FORM);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const isEditing = !!editingTest;

  useEffect(() => {
    if (editingTest) {
      setForm({
        title: editingTest.title,
        description: editingTest.description || '',
        cefr_level: editingTest.cefr_level,
        passing_score: editingTest.passing_score ?? 70,
        is_active: editingTest.is_active,
      });
    } else {
      setForm(DEFAULT_TEST_FORM);
    }
    setErrors({});
  }, [editingTest, isOpen]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!form.title.trim()) {
      newErrors.title = 'Sarlavha majburiy';
    } else if (form.title.trim().length < 3) {
      newErrors.title = 'Sarlavha kamida 3 ta belgidan iborat bolishi kerak';
    }

    if (form.passing_score < 0 || form.passing_score > 100) {
      newErrors.passing_score = 'Otish balli 0-100 oraligida bolishi kerak';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setSaving(true);
    try {
      if (isEditing && editingTest) {
        const payload: TestUpdate = {
          title: form.title.trim(),
          description: form.description.trim() || null,
          cefr_level: form.cefr_level,
          passing_score: form.passing_score,
          is_active: form.is_active,
        };
        await testsApi.update(editingTest.id, payload);
        toast.success('Test yangilandi');
      } else {
        const payload: TestCreate = {
          title: form.title.trim(),
          description: form.description.trim() || null,
          cefr_level: form.cefr_level,
          passing_score: form.passing_score,
          is_active: form.is_active,
        };
        await testsApi.create(payload);
        toast.success('Test yaratildi');
      }
      onSuccess();
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Saqlashda xatolik';
      toast.error(message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-x-4 top-[5%] md:inset-auto md:left-1/2 md:top-[10%] md:-translate-x-1/2 w-full md:max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden z-50 max-h-[90vh] flex flex-col"
          >
            {/* Header */}
            <div className="p-5 border-b border-slate-100 bg-gradient-to-r from-orange-500 to-orange-600 flex-shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-bold text-white">
                    {isEditing ? 'Testni tahrirlash' : 'Yangi test yaratish'}
                  </h2>
                  <p className="text-xs text-white/80">
                    {isEditing ? 'Mavjud testni ozgartiring' : 'CEFR testini yarating'}
                  </p>
                </div>
                <button
                  onClick={onClose}
                  disabled={saving}
                  className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition disabled:opacity-50"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Body */}
            <div className="p-5 space-y-5 overflow-y-auto flex-1">
              {/* Title */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                  Sarlavha <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  placeholder="Masalan: CEFR A1 Grammar Test"
                  className={`w-full px-4 py-2.5 border rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 transition-all ${
                    errors.title
                      ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
                      : 'border-slate-200 focus:border-orange-500 focus:ring-orange-500/20'
                  }`}
                />
                {errors.title && <p className="text-xs text-red-600 mt-1">{errors.title}</p>}
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                  Tavsif
                </label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  placeholder="Test haqida qisqa malumot..."
                  rows={3}
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all resize-none"
                />
              </div>

              {/* CEFR Level + Passing Score */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                    CEFR daraja <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={form.cefr_level}
                    onChange={(e) => setForm({ ...form, cefr_level: e.target.value as CefrLevel })}
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                  >
                    {CEFR_LEVELS.map((level) => (
                      <option key={level} value={level}>
                        {level}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                    Otish balli (%) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    value={form.passing_score}
                    onChange={(e) => setForm({ ...form, passing_score: Number(e.target.value) })}
                    min={0}
                    max={100}
                    className={`w-full px-4 py-2.5 border rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 transition-all ${
                      errors.passing_score
                        ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
                        : 'border-slate-200 focus:border-orange-500 focus:ring-orange-500/20'
                    }`}
                  />
                  {errors.passing_score && (
                    <p className="text-xs text-red-600 mt-1">{errors.passing_score}</p>
                  )}
                </div>
              </div>

              {/* Passing score preview */}
              <div className="p-3 bg-orange-50 border border-orange-100 rounded-xl">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-orange-700">Otish balli</span>
                  <span className="text-sm font-bold text-orange-800">{form.passing_score}%</span>
                </div>
                <div className="h-2 w-full bg-white rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-orange-400 to-orange-500 rounded-full transition-all duration-300"
                    style={{ width: `${form.passing_score}%` }}
                  />
                </div>
              </div>

              {/* Active Status */}
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200">
                <div>
                  <p className="text-sm font-semibold text-slate-900">Test holati</p>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {form.is_active
                      ? 'Test foydalanuvchilarga korsatiladi'
                      : 'Test yashirilgan holatda'}
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.is_active}
                    onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[] after:absolute after:top-[2px] after:right-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-orange-500 peer-checked:to-orange-600" />
                </label>
              </div>

              {/* Status indicator */}
              <div
                className={`flex items-center gap-2 p-3 rounded-xl border ${
                  form.is_active
                    ? 'bg-emerald-50 border-emerald-200'
                    : 'bg-slate-50 border-slate-200'
                }`}
              >
                {form.is_active ? (
                  <>
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                    <span className="text-sm font-medium text-emerald-800">Test faol</span>
                  </>
                ) : (
                  <>
                    <div className="w-4 h-4 text-slate-400" />
                    <span className="text-sm font-medium text-slate-600">Test ochirilgan</span>
                  </>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-slate-100 bg-slate-50 flex gap-2 flex-shrink-0">
              <button
                onClick={onClose}
                disabled={saving}
                className="flex-1 px-4 py-2.5 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-100 transition disabled:opacity-50"
              >
                Bekor qilish
              </button>
              <button
                onClick={handleSubmit}
                disabled={saving}
                className="flex-1 px-4 py-2.5 text-sm font-medium bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl hover:from-orange-600 hover:to-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-orange-500/20"
              >
                {saving
                  ? 'Saqlanmoqda...'
                  : isEditing
                  ? 'Yangilash'
                  : 'Yaratish'}
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}