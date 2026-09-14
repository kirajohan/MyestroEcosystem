'use client';

import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Plus, Trash2, CheckCircle2, FileQuestion } from 'lucide-react';
import {
  TestQuestion,
  QuestionCreate,
  QuestionUpdate,
  QuestionFormState,
  DEFAULT_QUESTION_FORM,
} from '@/types/test';
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

  useEffect(() => {
    if (editingQuestion) {
      const optionsStrings = editingQuestion.options.map((opt: any) => {
        if (typeof opt === 'string') return opt;
        if (typeof opt === 'object' && opt !== null) {
          return opt.text || opt.label || '';
        }
        return String(opt);
      });

      let correctIdx = editingQuestion.correct_option_index ?? 0;

      if (editingQuestion.correct_answer) {
        correctIdx = editingQuestion.correct_answer.charCodeAt(0) - 65;
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
      toast.error(`Kamida ${MIN_OPTIONS} ta variant bolishi kerak`);
      return;
    }

    const newOptions = form.options.filter((_, i) => i !== index);
    let newCorrectIndex = form.correct_option_index;

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

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!form.question_text.trim()) {
      newErrors.question_text = 'Savol matni majburiy';
    }

    const filledOptions = form.options.filter((opt) => opt.trim());
    if (filledOptions.length < MIN_OPTIONS) {
      newErrors.options = `Kamida ${MIN_OPTIONS} ta variant toldirilishi kerak`;
    }

    if (!form.options[form.correct_option_index]?.trim()) {
      newErrors.correct = 'Togri javob sifatida toldirilgan variantni tanlang';
    }

    const uniqueOptions = new Set(filledOptions.map((o) => o.trim().toLowerCase()));
    if (uniqueOptions.size !== filledOptions.length) {
      newErrors.options = 'Variantlar takrorlanmasligi kerak';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    setSaving(true);
    try {
      const cleanOptions = form.options.filter((opt) => opt.trim());
      const originalCorrectText = form.options[form.correct_option_index]?.trim();
      const newCorrectIndex = cleanOptions.findIndex((opt) => opt.trim() === originalCorrectText);

      const optionsForBackend = cleanOptions.map((optText, idx) => ({
        text: optText,
        label: String.fromCharCode(65 + idx),
        is_correct: idx === newCorrectIndex,
      }));

      if (isEditing && editingQuestion) {
        const payload: QuestionUpdate = {
          question_text: form.question_text.trim(),
          options: optionsForBackend as any,
          correct_option_index: newCorrectIndex,
          explanation: form.explanation.trim() || null,
        };
        await testsApi.updateQuestion(testId, editingQuestion.id, payload);
        toast.success('Savol yangilandi');
      } else {
        const payload: QuestionCreate = {
          question_text: form.question_text.trim(),
          options: optionsForBackend as any,
          correct_option_index: newCorrectIndex,
          explanation: form.explanation.trim() || null,
          order_index: nextOrderIndex,
        };
        await testsApi.addQuestion(testId, payload);
        toast.success('Savol qoshildi');
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
            className="fixed inset-x-4 top-[5%] md:inset-auto md:left-1/2 md:top-[8%] md:-translate-x-1/2 w-full md:max-w-2xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden z-50 max-h-[90vh] flex flex-col"
          >
            {/* Header */}
            <div className="p-5 border-b border-slate-100 bg-gradient-to-r from-orange-500 to-orange-600 flex-shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                  <FileQuestion className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h2 className="text-lg font-bold text-white">
                    {isEditing ? 'Savolni tahrirlash' : 'Yangi savol qoshish'}
                  </h2>
                  <p className="text-xs text-white/80">
                    {isEditing ? 'Mavjud savolni ozgartiring' : 'Testga yangi savol qoshing'}
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
              {/* Question Text */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                  Savol matni <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={form.question_text}
                  onChange={(e) => setForm({ ...form, question_text: e.target.value })}
                  placeholder="Masalan: Choose the correct verb form..."
                  rows={3}
                  className={`w-full px-4 py-2.5 border rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 transition-all resize-none ${
                    errors.question_text
                      ? 'border-red-300 focus:border-red-500 focus:ring-red-500/20'
                      : 'border-slate-200 focus:border-orange-500'
                  }`}
                />
                {errors.question_text && (
                  <p className="text-xs text-red-600 mt-1">{errors.question_text}</p>
                )}
              </div>

              {/* Options */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-semibold text-slate-900">
                    Variantlar <span className="text-red-500">*</span>
                  </label>
                  <button
                    onClick={handleAddOption}
                    disabled={form.options.length >= MAX_OPTIONS}
                    className="inline-flex items-center gap-1 text-xs text-orange-600 hover:text-orange-700 font-medium disabled:opacity-50 transition-colors"
                  >
                    <Plus size={12} />
                    Variant qoshish
                  </button>
                </div>

                <div className="space-y-2">
                  {form.options.map((option, idx) => {
                    const letter = String.fromCharCode(65 + idx);
                    const isCorrect = form.correct_option_index === idx;

                    return (
                      <div key={idx} className="flex items-center gap-2">
                        {/* Radio for correct answer */}
                        <button
                          type="button"
                          onClick={() => handleCorrectChange(idx)}
                          className={`flex-shrink-0 w-8 h-8 rounded-lg border-2 flex items-center justify-center transition-all text-xs font-bold ${
                            isCorrect
                              ? 'border-emerald-500 bg-emerald-500 text-white shadow-sm shadow-emerald-500/20'
                              : 'border-slate-200 bg-white text-slate-400 hover:border-emerald-400 hover:text-emerald-500'
                          }`}
                          title="Togri javob sifatida belgilash"
                        >
                          {letter}
                        </button>

                        {/* Option input */}
                        <input
                          type="text"
                          value={option}
                          onChange={(e) => handleOptionChange(idx, e.target.value)}
                          placeholder={`Variant ${idx + 1}`}
                          className={`flex-1 px-3 py-2 border rounded-xl text-sm focus:outline-none focus:ring-2 transition-all ${
                            isCorrect
                              ? 'border-emerald-300 bg-emerald-50 focus:ring-emerald-500/20'
                              : 'border-slate-200 bg-slate-50 focus:ring-orange-500/20 focus:border-orange-500'
                          }`}
                        />

                        {/* Remove button */}
                        {form.options.length > MIN_OPTIONS && (
                          <button
                            type="button"
                            onClick={() => handleRemoveOption(idx)}
                            className="flex-shrink-0 p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                            title="Variantni ochirish"
                          >
                            <Trash2 size={14} />
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>

                {errors.options && <p className="text-xs text-red-600 mt-2">{errors.options}</p>}
                {errors.correct && <p className="text-xs text-red-600 mt-2">{errors.correct}</p>}

                <div className="flex items-start gap-2 mt-3 p-3 bg-blue-50 border border-blue-100 rounded-xl">
                  <CheckCircle2 size={14} className="text-blue-500 mt-0.5 flex-shrink-0" />
                  <p className="text-xs text-blue-800 leading-relaxed">
                    Harf ustiga bosib togri javobni belgilang. Telegram Quiz Poll da togri javob yashil rangda korsatiladi.
                  </p>
                </div>
              </div>

              {/* Explanation */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                  Izoh (ixtiyoriy)
                </label>
                <textarea
                  value={form.explanation}
                  onChange={(e) => setForm({ ...form, explanation: e.target.value })}
                  placeholder="Javob haqida qoshimcha izoh... (foydalanuvchi javob bergandan keyin korsatiladi)"
                  rows={2}
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all resize-none"
                />
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
                  : 'Savolni qoshish'}
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}