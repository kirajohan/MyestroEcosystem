// admin/components/tests/TestFormModal.tsx
'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { X } from 'lucide-react';
import { Test, TestCreate, TestUpdate, CefrLevel, CEFR_LEVELS, TestFormState, DEFAULT_TEST_FORM } from '@/types/test';
import { testsApi, ApiError } from '@/lib/api_client';

interface TestFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  editingTest: Test | null;
}

export default function TestFormModal({ isOpen, onClose, onSuccess, editingTest }: TestFormModalProps) {
  const [form, setForm] = useState<TestFormState>(DEFAULT_TEST_FORM);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const isEditing = !!editingTest;

  // Form'ni editingTest bilan to'ldirish
  useEffect(() => {
    if (editingTest) {
      setForm({
        title: editingTest.title,
        description: editingTest.description || '',
        cefr_level: editingTest.cefr_level,
        passing_score: editingTest.passing_score,
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
      newErrors.title = 'Sarlavha kamida 3 ta belgidan iborat bo&apos;lishi kerak';
    }

    if (form.passing_score < 0 || form.passing_score > 100) {
      newErrors.passing_score = "O&apos;tish balli 0-100 oralig&apos;ida bo&apos;lishi kerak";
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
        toast.success('✅ Test yangilandi!');
      } else {
        const payload: TestCreate = {
          title: form.title.trim(),
          description: form.description.trim() || null,
          cefr_level: form.cefr_level,
          passing_score: form.passing_score,
          is_active: form.is_active,
        };
        await testsApi.create(payload);
        toast.success('✅ Test yaratildi!');
      }
      onSuccess();
    } catch (err) {
      const message = err instanceof ApiError ? err.message : 'Saqlashda xatolik';
      toast.error(message);
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            {isEditing ? 'Testni tahrirlash' : 'Yangi test yaratish'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sarlavha <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="Masalan: CEFR A1 Grammar Test"
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.title ? 'border-red-300 bg-red-50' : 'border-gray-300'
              }`}
            />
            {errors.title && <p className="text-xs text-red-500 mt-1">{errors.title}</p>}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tavsif</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Test haqida qisqa ma'lumot..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>

          {/* CEFR Level + Passing Score */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                CEFR daraja <span className="text-red-500">*</span>
              </label>
              <select
                value={form.cefr_level}
                onChange={(e) => setForm({ ...form, cefr_level: e.target.value as CefrLevel })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              >
                {CEFR_LEVELS.map((level) => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                O&apos;tish balli (%) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={form.passing_score}
                onChange={(e) => setForm({ ...form, passing_score: Number(e.target.value) })}
                min={0}
                max={100}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.passing_score ? 'border-red-300 bg-red-50' : 'border-gray-300'
                }`}
              />
              {errors.passing_score && (
                <p className="text-xs text-red-500 mt-1">{errors.passing_score}</p>
              )}
            </div>
          </div>

          {/* Active Status */}
          <div className="flex items-center gap-3 pt-2">
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:right-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600" />
            </label>
            <span className="text-sm text-gray-700">
              {form.is_active ? '✅ Faol' : '❌ O&apos;chirilgan'}
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-5 border-t border-gray-200 bg-gray-50 rounded-b-xl">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Bekor qilish
          </button>
          <button
            onClick={handleSubmit}
            disabled={saving}
            className="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {saving ? 'Saqlanmoqda...' : isEditing ? 'Yangilash' : 'Yaratish'}
          </button>
        </div>
      </div>
    </div>
  );
}
