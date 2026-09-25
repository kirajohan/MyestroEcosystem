'use client';

import { useCallback, useEffect, useState, FormEvent } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Trash2,
  Plus,
  CheckCircle2,
  Save,
  Loader2,
  AlertCircle,
  BookOpen,
  Headphones,
  PenTool,
  Mic,
} from 'lucide-react';
import AudioUpload from '@/app/exam/components/AudioUpload';
import { toast } from 'sonner';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://myestroeco-backend-production.up.railway.app';

interface Option {
  id?: number;
  text: string;
  is_correct: boolean;
  order: number;
}

interface Item {
  id: number;
  item_type: string;
  title: string;
  instruction?: string;
  question_text?: string;
  passage_text?: string;
  audio_url?: string;
  max_score: number;
  order: number;
  options: Option[];
  answer_key?: any;
}

export default function ItemEditPage() {
  const router = useRouter();
  const params = useParams();
  const examId = Number(params.id);
  const blockId = Number(params.blockId);
  const itemId = params.itemId === 'new' ? null : Number(params.itemId);
  const { token } = useAuth();

  const [loading, setLoading] = useState(!!itemId);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    item_type: 'reading_question',
    title: '',
    instruction: '',
    question_text: '',
    passage_text: '',
    audio_url: '',
    max_score: 1,
    order: 1,
  });

  const [options, setOptions] = useState<Option[]>([
    { text: '', is_correct: false, order: 1 },
    { text: '', is_correct: false, order: 2 },
    { text: '', is_correct: false, order: 3 },
    { text: '', is_correct: false, order: 4 },
  ]);

  const loadItem = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v2/exam/admin/blocks/${blockId}/items`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Yuklanmadi');
      const items = await res.json();
      const item = items.find((i: Item) => i.id === itemId);
      if (item) {
        setFormData({
          item_type: item.item_type,
          title: item.title || '',
          instruction: item.instruction || '',
          question_text: item.question_text || '',
          passage_text: item.passage_text || '',
          audio_url: item.audio_url || '',
          max_score: item.max_score || 1,
          order: item.order || 1,
        });
        if (item.options && item.options.length > 0) {
          setOptions(item.options.map((o: Option) => ({ ...o })));
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Xato');
    } finally {
      setLoading(false);
    }
  }, [token, blockId, itemId]);

  useEffect(() => {
    if (itemId && token) loadItem();
  }, [itemId, token, loadItem]);

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? Number(value) : value,
    }));
  }

  function handleOptionChange(idx: number, field: 'text' | 'is_correct', value: string | boolean) {
    setOptions((prev) => prev.map((opt, i) => (i === idx ? { ...opt, [field]: value } : opt)));
  }

  function handleAddOption() {
    setOptions((prev) => [...prev, { text: '', is_correct: false, order: prev.length + 1 }]);
  }

  function handleRemoveOption(idx: number) {
    setOptions((prev) => prev.filter((_, i) => i !== idx));
  }

  function handleAudioUploaded(url: string) {
    setFormData((prev) => ({ ...prev, audio_url: url }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      const correctIds = options
        .map((opt, idx) => (opt.is_correct ? idx + 1 : null))
        .filter((id) => id !== null);

      const payload = {
        ...formData,
        audio_file_id: formData.audio_url,
        audio_url: null,
        options: options.filter((o) => o.text.trim()),
        answer_key: { correct_option_ids: correctIds },
      };

      const url = itemId
        ? `${API_URL}/api/v2/exam/admin/items/${itemId}`
        : `${API_URL}/api/v2/exam/admin/blocks/${blockId}/items`;
      const method = itemId ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `HTTP ${res.status}`);
      }

      toast.success(itemId ? 'Savol yangilandi' : 'Savol yaratildi');
      router.push(`/exam/exams/${examId}/blocks/${blockId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Saqlashda xato');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
      </div>
    );
  }

  const hasAudio = formData.item_type === 'listening_question';
  const hasPassage = formData.item_type === 'reading_question';

  return (
    <div className="p-4 md:p-6 max-w-4xl mx-auto">
      <button
        onClick={() => router.push(`/exam/exams/${examId}/blocks/${blockId}`)}
        className="flex items-center gap-2 text-sm text-slate-600 hover:text-orange-600 transition-colors mb-4"
      >
        <ArrowLeft className="w-4 h-4" />
        Blockga qaytish
      </button>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
      >
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-5">
          <h1 className="text-xl font-bold text-white">
            {itemId ? 'Savolni tahrirlash' : 'Yangi savol qoshish'}
          </h1>
          <p className="text-sm text-white/80 mt-1">Block #{blockId}</p>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-5">
          <div>
            <label className="block text-sm font-semibold text-slate-900 mb-1.5">Savol turi</label>
            <select
              name="item_type"
              value={formData.item_type}
              onChange={handleChange}
              className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
            >
              <option value="reading_question">Reading Question</option>
              <option value="listening_question">Listening Question</option>
              <option value="writing_task">Writing Task</option>
              <option value="speaking_task">Speaking Task</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-900 mb-1.5">
              Sarlavha <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              placeholder="Masalan: Question 1"
              className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
            />
          </div>

          {hasAudio && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-blue-900 mb-3 flex items-center gap-2">
                <Headphones className="w-4 h-4" />
                Audio fayl
              </h3>
              <AudioUpload currentUrl={formData.audio_url} onUpload={handleAudioUploaded} />
            </div>
          )}

          {hasPassage && (
            <div>
              <label className="block text-sm font-semibold text-slate-900 mb-1.5 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-emerald-600" />
                Passage (matn)
              </label>
              <textarea
                name="passage_text"
                value={formData.passage_text}
                onChange={handleChange}
                rows={6}
                placeholder="Reading uchun matn..."
                className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all font-mono resize-y"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-semibold text-slate-900 mb-1.5">
              Savol matni <span className="text-red-500">*</span>
            </label>
            <textarea
              name="question_text"
              value={formData.question_text}
              onChange={handleChange}
              required
              rows={2}
              placeholder="What is the main idea?"
              className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all resize-none"
            />
          </div>

          {(formData.item_type === 'reading_question' ||
            formData.item_type === 'listening_question') && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-semibold text-slate-900">Variantlar</label>
                <button
                  type="button"
                  onClick={handleAddOption}
                  className="flex items-center gap-1 text-xs text-orange-600 hover:text-orange-700 font-medium"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Variant
                </button>
              </div>

              <div className="space-y-2">
                {options.map((opt, idx) => {
                  const letter = String.fromCharCode(65 + idx);
                  const isCorrect = opt.is_correct;

                  return (
                    <div key={idx} className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => handleOptionChange(idx, 'is_correct', !opt.is_correct)}
                        className={`flex-shrink-0 w-9 h-9 rounded-lg border-2 flex items-center justify-center transition-all text-xs font-bold ${
                          isCorrect
                            ? 'border-emerald-500 bg-emerald-500 text-white'
                            : 'border-slate-200 bg-white text-slate-400'
                        }`}
                      >
                        {letter}
                      </button>
                      <input
                        type="text"
                        value={opt.text}
                        onChange={(e) => handleOptionChange(idx, 'text', e.target.value)}
                        placeholder={`Variant ${letter}`}
                        className="flex-1 px-3 py-2 border border-slate-200 rounded-xl bg-slate-50 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                      />
                      {options.length > 2 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveOption(idx)}
                          className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-slate-900 mb-1.5">Tartib</label>
              <input
                type="number"
                name="order"
                value={formData.order}
                onChange={handleChange}
                min={1}
                className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-900 mb-1.5">Maks ball</label>
              <input
                type="number"
                name="max_score"
                value={formData.max_score}
                onChange={handleChange}
                min={0}
                step={0.5}
                className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
              />
            </div>
          </div>

          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-xl">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <div className="flex gap-2 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => router.push(`/exam/exams/${examId}/blocks/${blockId}`)}
              className="px-6 py-2.5 border border-slate-200 text-slate-700 rounded-xl hover:bg-slate-50 font-medium text-sm transition"
            >
              Bekor qilish
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl font-semibold hover:from-orange-600 hover:to-orange-700 disabled:opacity-50 transition-all shadow-lg shadow-orange-500/20"
            >
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Saqlanmoqda...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Saqlash
                </>
              )}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}