// admin/components/tests/QuestionFormModal.tsx
'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { X, Plus, Trash2, CheckCircle2 } from 'lucide-react';
import { TestQuestion, QuestionCreate, QuestionUpdate, QuestionFormState, DEFAULT_QUESTION_FORM } from '@/types/test';
import { testsApi, ApiError } from '@/lib/api_client';

interface QuestionFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  testId: number;
  editingQuestion: TestQuestion | null;
  nextOrderIndex: number;
}

const MIN_OPTIONS = 2;
const MAX_OPTIONS = 10;

export default function QuestionFormModal({
  isOpen,
  onClose,
  onSuccess,
  testId,
  editingQuestion,
  nextOrderIndex,
}: QuestionFormModalProps) {
  const [form, setForm] = useState<QuestionFormState>(DEFAULT_QUESTION_FORM);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const isEditing = !!editingQuestion;

  // Form'ni editingQuestion bilan to'ldirish
// Form'ni editingQuestion bilan to'ldirish
useEffect(() => {
  if (editingQuestion) {
    // ✅ Options formatini tekshirish va string array'ga o'tkazish
    const optionsStrings = editingQuestion.options.map((opt: any) => {
      if (typeof opt === 'string') return opt;
      if (typeof opt === 'object' && opt !== null) {
        return opt.text || opt.label || '';
      }
      return String(opt);
    });

    // ✅ To'g'ri javob indeksini topish
    let correctIdx = editingQuestion.correct_option_index ?? 0;
    
    if (editingQuestion.correct_answer) {
      // "A" → 0, "B" → 1
      correctIdx = editingQuestion.correct_answer.charCodeAt(0) - 'A'.charCodeAt(0);
    } else if (Array.isArray(editingQuestion.options) && editingQuestion.options.length > 0) {
      const foundIdx = editingQuestion.options.findIndex((opt: any) => {
        if (typeof opt === 'object' && opt !== null) {
          return opt.is_correct === true;
        }
        return false;
      });
      if (foundIdx !== -1) correctIdx = foundIdx;
    }

    setForm({
      question_text: editingQuestion.question_text,
      options: optionsStrings,
      correct_option_index: correctIdx,
      explanation: editingQuestion.explanation || '',
    });
  } else {
    setForm(DEFAULT_QUESTION_FORM);
  }
  setErrors({});
}, [editingQuestion, isOpen]);


  // ─── Option Handlers ─────────────────────────────────────
  const handleOptionChange = (index: number, value: string) => {
    const newOptions = [...form.options];
    newOptions[index] = value;
    setForm({ ...form, options: newOptions });
  };

  const handleAddOption = () => {
    if (form.options.length >= MAX_OPTIONS) {
      toast.error(`Maksimal ${MAX_OPTIONS} ta variant mumkin`);
      return;
    }
    setForm({ ...form, options: [...form.options, ''] });
  };

  const handleRemoveOption = (index: number) => {
    if (form.options.length <= MIN_OPTIONS) {
      toast.error(`Kamida ${MIN_OPTIONS} ta variant bo&apos;lishi kerak`);
      return;
    }

    const newOptions = form.options.filter((_, i) => i !== index);
    let newCorrectIndex = form.correct_option_index;

    // Agar o'chirilgan variant to'g'ri javob bo'lsa
    if (index === form.correct_option_index) {
      newCorrectIndex = 0;
    } else if (index < form.correct_option_index) {
      newCorrectIndex = form.correct_option_index - 1;
    }

    setForm({
      ...form,
      options: newOptions,
      correct_option_index: newCorrectIndex,
    });
  };

  const handleCorrectChange = (index: number) => {
    setForm({ ...form, correct_option_index: index });
  };

  // ─── Validation ──────────────────────────────────────────
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!form.question_text.trim()) {
      newErrors.question_text = 'Savol matni majburiy';
    }

    const filledOptions = form.options.filter((opt) => opt.trim());
    if (filledOptions.length < MIN_OPTIONS) {
      newErrors.options = `Kamida ${MIN_OPTIONS} ta variant to&apos;ldirilishi kerak`;
    }

    // To'g'ri javob tanlangan variant ichida bo'lishi kerak
    if (!form.options[form.correct_option_index]?.trim()) {
      newErrors.correct = "To&apos;g&apos;ri javob sifatida to&apos;ldirilgan variantni tanlang";
    }

    // Duplicate variant tekshiruvi
    const uniqueOptions = new Set(filledOptions.map((o) => o.trim().toLowerCase()));
    if (uniqueOptions.size !== filledOptions.length) {
      newErrors.options = 'Variantlar takrorlanmasligi kerak';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ─── Submit ──────────────────────────────────────────────
const handleSubmit = async () => {
  if (!validate()) return;

  setSaving(true);
  try {
    // Bo'sh variantlarni olib tashlash
    const cleanOptions = form.options.filter((opt) => opt.trim());
    const originalCorrectText = form.options[form.correct_option_index]?.trim();
    const newCorrectIndex = cleanOptions.findIndex(
      (opt) => opt.trim() === originalCorrectText
    );

    // ✅ Backend options formatini moslashtirish
    // Backend object array kutmoqda: [{text, label, is_correct}]
    const optionsForBackend = cleanOptions.map((optText, idx) => ({
      text: optText,
      label: String.fromCharCode(65 + idx), // A, B, C, D
      is_correct: idx === newCorrectIndex,
    }));

    if (isEditing && editingQuestion) {
      const payload: QuestionUpdate = {
        question_text: form.question_text.trim(),
        options: optionsForBackend as any, // ✅ Object array yuboramiz
        correct_option_index: newCorrectIndex,
        explanation: form.explanation.trim() || null,
      };
      await testsApi.updateQuestion(testId, editingQuestion.id, payload);
      toast.success('✅ Savol yangilandi!');
    } else {
      const payload: QuestionCreate = {
        question_text: form.question_text.trim(),
        options: optionsForBackend as any, // ✅ Object array yuboramiz
        correct_option_index: newCorrectIndex,
        explanation: form.explanation.trim() || null,
        order_index: nextOrderIndex,
      };
      await testsApi.addQuestion(testId, payload);
      toast.success('✅ Savol qoshildi!');
    }
    onSuccess();
  } catch (err) {
    const message = err instanceof ApiError ? err.message : 'Saqlashda xatolik';
    toast.error(message);
  } finally {
    setSaving(false);
  }
}

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-gray-200 sticky top-0 bg-white z-10">
          <h2 className="text-lg font-semibold text-gray-900">
            {isEditing ? 'Savolni tahrirlash' : 'Yangi savol qo&apos;shish'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-5">
          {/* Question Text */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Savol matni <span className="text-red-500">*</span>
            </label>
            <textarea
              value={form.question_text}
              onChange={(e) => setForm({ ...form, question_text: e.target.value })}
              placeholder="Masalan: Choose the correct verb form..."
              rows={3}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${
                errors.question_text ? 'border-red-300 bg-red-50' : 'border-gray-300'
              }`}
            />
            {errors.question_text && (
              <p className="text-xs text-red-500 mt-1">{errors.question_text}</p>
            )}
          </div>

          {/* Options */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Variantlar <span className="text-red-500">*</span>
              </label>
              <button
                onClick={handleAddOption}
                disabled={form.options.length >= MAX_OPTIONS}
                className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 font-medium disabled:opacity-50"
              >
                <Plus size={12} />
                Variant qo&apos;shish
              </button>
            </div>

            <div className="space-y-2">
              {form.options.map((option, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  {/* Radio for correct answer */}
                  <button
                    type="button"
                    onClick={() => handleCorrectChange(idx)}
                    className={`flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${
                      form.correct_option_index === idx
                        ? 'border-green-500 bg-green-500'
                        : 'border-gray-300 hover:border-green-400'
                    }`}
                    title="To&apos;g&apos;ri javob sifatida belgilash"
                  >
                    {form.correct_option_index === idx && (
                      <CheckCircle2 size={12} className="text-white" />
                    )}
                  </button>

                  {/* Option input */}
                  <input
                    type="text"
                    value={option}
                    onChange={(e) => handleOptionChange(idx, e.target.value)}
                    placeholder={`Variant ${idx + 1}`}
                    className={`flex-1 px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      form.correct_option_index === idx
                        ? 'border-green-300 bg-green-50'
                        : 'border-gray-300'
                    }`}
                  />

                  {/* Remove button */}
                  {form.options.length > MIN_OPTIONS && (
                    <button
                      type="button"
                      onClick={() => handleRemoveOption(idx)}
                      className="flex-shrink-0 p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                      title="Variantni o&apos;chirish"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              ))}
            </div>

            {errors.options && (
              <p className="text-xs text-red-500 mt-1">{errors.options}</p>
            )}
            {errors.correct && (
              <p className="text-xs text-red-500 mt-1">{errors.correct}</p>
            )}

            <p className="text-xs text-gray-400 mt-2">
              💡 Yashil doira ustiga bosib to&apos;g&apos;ri javobni belgilang. Telegram Quiz Poll&apos;da to&apos;g&apos;ri javob yashil rangda ko&apos;rsatiladi.
            </p>
          </div>

          {/* Explanation */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Izoh (ixtiyoriy)
            </label>
            <textarea
              value={form.explanation}
              onChange={(e) => setForm({ ...form, explanation: e.target.value })}
              placeholder="Javob haqida qo'shimcha izoh... (foydalanuvchi javob bergandan keyin ko'rsatiladi)"
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-5 border-t border-gray-200 bg-gray-50 rounded-b-xl sticky bottom-0">
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
            {saving ? 'Saqlanmoqda...' : isEditing ? 'Yangilash' : "Savolni qo&apos;shish"}
          </button>
        </div>
      </div>
    </div>
  );
}
