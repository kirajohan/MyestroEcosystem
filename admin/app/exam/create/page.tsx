'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Shuffle,
  Save,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Headphones,
  BookOpen,
  PenTool,
  Mic,
  Target,
  Clock,
  Sparkles,
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

const EXAM_TYPES = [
  { value: 'full', label: 'Full Exam', description: 'Listening + Reading + Writing + Speaking', icon: Target, color: 'orange' },
  { value: 'listening', label: 'Listening', description: 'Tinglash malakasi', icon: Headphones, color: 'blue' },
  { value: 'reading', label: 'Reading', description: 'Oqish malakasi', icon: BookOpen, color: 'emerald' },
  { value: 'writing', label: 'Writing', description: 'Yozish malakasi', icon: PenTool, color: 'purple' },
  { value: 'speaking', label: 'Speaking', description: 'Gapirish malakasi', icon: Mic, color: 'rose' },
];

const CEFR_LEVELS = [
  { value: 'A1', label: 'A1', color: 'emerald', description: 'Beginner' },
  { value: 'A2', label: 'A2', color: 'teal', description: 'Elementary' },
  { value: 'B1', label: 'B1', color: 'blue', description: 'Intermediate' },
  { value: 'B2', label: 'B2', color: 'indigo', description: 'Upper-Int.' },
  { value: 'C1', label: 'C1', color: 'purple', description: 'Advanced' },
  { value: 'C2', label: 'C2', color: 'rose', description: 'Proficient' },
];

export default function CreateExamPage() {
  const router = useRouter();
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [timeLimitMin, setTimeLimitMin] = useState(30);

  const [formData, setFormData] = useState({
    code: '',
    title: '',
    description: '',
    exam_type: 'reading',
    cefr_level: 'B1',
    is_published: false,
  });

  function generateCode() {
    const code = `${formData.exam_type}_${formData.cefr_level.toLowerCase()}_${Date.now().toString(36).slice(-4)}`;
    setFormData((prev) => ({ ...prev, code }));
  }

  function handleChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (!token) {
        setError('Token topilmadi. Qayta login qiling.');
        return;
      }

      const res = await fetch(`${API_URL}/api/v2/exam/admin/exams`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...formData,
          time_limit_sec: timeLimitMin * 60,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `HTTP ${res.status}`);
      }

      const created = await res.json();
      toast.success(`Exam yaratildi: ${created.code}`);
      router.push(`/exam/exams/${created.id}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Nomalum xato';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  const selectedType = EXAM_TYPES.find((t) => t.value === formData.exam_type);
  const SelectedTypeIcon = selectedType?.icon || Target;

  return (
    <div className="space-y-6">
      {/* Back button + Header */}
      <div className="flex flex-col gap-2">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-sm text-slate-600 hover:text-orange-600 transition-colors w-fit"
        >
          <ArrowLeft className="w-4 h-4" />
          Orqaga
        </button>

        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Yangi Exam yaratish</h1>
          <p className="text-sm md:text-base text-slate-600 mt-1">
            Imtihon parametrlarini belgilang va blocklarni keyinchalik qoshing
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Exam Type Selection */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
        >
          <div className="p-5 border-b border-slate-100">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Target className="w-5 h-5 text-orange-500" />
              Exam turi
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">Qaysi malaka turini tekshirmoqchisiz?</p>
          </div>

          <div className="p-5">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {EXAM_TYPES.map((type) => {
                const Icon = type.icon;
                const isSelected = formData.exam_type === type.value;
                const colorMap: Record<string, string> = {
                  orange: 'from-orange-500 to-orange-600 border-orange-500',
                  blue: 'from-blue-500 to-blue-600 border-blue-500',
                  emerald: 'from-emerald-500 to-emerald-600 border-emerald-500',
                  purple: 'from-purple-500 to-purple-600 border-purple-500',
                  rose: 'from-rose-500 to-rose-600 border-rose-500',
                };

                return (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => setFormData((prev) => ({ ...prev, exam_type: type.value }))}
                    className={`relative p-4 rounded-xl border-2 transition-all text-left ${
                      isSelected
                        ? `${colorMap[type.color]} bg-gradient-to-br text-white shadow-lg`
                        : 'border-slate-200 bg-white hover:border-slate-300'
                    }`}
                  >
                    <Icon
                      className={`w-6 h-6 mb-2 ${isSelected ? 'text-white' : 'text-slate-500'}`}
                    />
                    <p
                      className={`font-semibold text-sm ${
                        isSelected ? 'text-white' : 'text-slate-900'
                      }`}
                    >
                      {type.label}
                    </p>
                    <p
                      className={`text-xs mt-0.5 ${
                        isSelected ? 'text-white/80' : 'text-slate-500'
                      }`}
                    >
                      {type.description}
                    </p>
                    {isSelected && (
                      <div className="absolute top-2 right-2">
                        <CheckCircle2 className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </motion.div>

        {/* CEFR Level */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
        >
          <div className="p-5 border-b border-slate-100">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-orange-500" />
              CEFR daraja
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">Imtihon qaysi darajaga mojaljallangan?</p>
          </div>

          <div className="p-5">
            <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
              {CEFR_LEVELS.map((level) => {
                const isSelected = formData.cefr_level === level.value;
                return (
                  <button
                    key={level.value}
                    type="button"
                    onClick={() => setFormData((prev) => ({ ...prev, cefr_level: level.value }))}
                    className={`p-3 rounded-xl border-2 transition-all text-center ${
                      isSelected
                        ? 'border-orange-500 bg-orange-50 shadow-sm'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <p
                      className={`text-lg font-bold ${
                        isSelected ? 'text-orange-600' : 'text-slate-900'
                      }`}
                    >
                      {level.label}
                    </p>
                    <p className="text-[10px] text-slate-500 mt-0.5">{level.description}</p>
                  </button>
                );
              })}
            </div>
          </div>
        </motion.div>

        {/* Basic Info */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
        >
          <div className="p-5 border-b border-slate-100">
            <h2 className="text-base font-bold text-slate-900">Asosiy malumotlar</h2>
          </div>

          <div className="p-5 space-y-4">
            {/* Code */}
            <div>
              <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                Kod <span className="text-red-500">*</span>
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  name="code"
                  value={formData.code}
                  onChange={handleChange}
                  required
                  placeholder="reading_b1_mock_01"
                  className="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all font-mono"
                />
                <button
                  type="button"
                  onClick={generateCode}
                  className="flex items-center gap-2 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-medium transition"
                  title="Avtomatik yaratish"
                >
                  <Shuffle className="w-4 h-4" />
                  <span className="hidden sm:inline">Auto</span>
                </button>
              </div>
              <p className="text-xs text-slate-500 mt-1">Unikal kod bolishi kerak</p>
            </div>

            {/* Title */}
            <div>
              <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                Nomi <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
                placeholder="Masalan: Reading Practice B1 - Technology"
                className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                Tavsif
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={3}
                placeholder="Imtihon haqida qisqa malumot..."
                className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all resize-none"
              />
            </div>

            {/* Time Limit */}
            <div>
              <label className="block text-sm font-semibold text-slate-900 mb-1.5 flex items-center gap-2">
                <Clock className="w-4 h-4 text-orange-500" />
                Vaqt (daqiqa) <span className="text-red-500">*</span>
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min={5}
                  max={300}
                  step={5}
                  value={timeLimitMin}
                  onChange={(e) => setTimeLimitMin(Number(e.target.value))}
                  className="flex-1 accent-orange-500"
                />
                <div className="w-20 px-3 py-2 bg-orange-50 border border-orange-200 rounded-lg text-center">
                  <span className="text-sm font-bold text-orange-700">{timeLimitMin}</span>
                  <span className="text-xs text-orange-600 ml-1">daq</span>
                </div>
              </div>
              <div className="flex justify-between text-xs text-slate-500 mt-1 px-1">
                <span>5 daq</span>
                <span>300 daq (5 soat)</span>
              </div>
            </div>

            {/* Publish toggle */}
            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200">
              <div>
                <p className="text-sm font-semibold text-slate-900">Darhol nashr qilish</p>
                <p className="text-xs text-slate-500 mt-0.5">
                  {formData.is_published
                    ? 'Foydalanuvchilar examni korishi mumkin'
                    : 'Exam qoralama holatda qoladi'}
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  name="is_published"
                  checked={formData.is_published}
                  onChange={handleChange}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-slate-300 rounded-full peer peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[] after:absolute after:top-[2px] after:right-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-orange-500 peer-checked:to-orange-600" />
              </label>
            </div>
          </div>
        </motion.div>

        {/* Error */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-xl"
          >
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700 flex-1">{error}</p>
          </motion.div>
        )}

        {/* Preview Card */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl p-5 text-white shadow-xl"
        >
          <p className="text-xs text-white/60 uppercase tracking-wider mb-3">Korinish</p>
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center shadow-lg shadow-orange-500/30 flex-shrink-0">
              <SelectedTypeIcon className="w-7 h-7 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-bold truncate">
                {formData.title || 'Nomsiz exam'}
              </h3>
              <p className="text-sm text-white/70 font-mono mt-0.5">
                {formData.code || 'code-yoq'}
              </p>
              <div className="flex flex-wrap items-center gap-2 mt-2">
                <span className="px-2 py-0.5 bg-white/10 rounded text-xs font-medium">
                  {formData.cefr_level}
                </span>
                <span className="px-2 py-0.5 bg-white/10 rounded text-xs font-medium">
                  {timeLimitMin} daqiqa
                </span>
                <span
                  className={`px-2 py-0.5 rounded text-xs font-medium ${
                    formData.is_published
                      ? 'bg-emerald-500 text-white'
                      : 'bg-white/10 text-white/80'
                  }`}
                >
                  {formData.is_published ? 'Published' : 'Draft'}
                </span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-2 pt-4 border-t border-slate-200">
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-3 border border-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-50 transition"
          >
            Bekor qilish
          </button>
          <button
            type="submit"
            disabled={loading}
            className="flex-1 flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl font-semibold hover:from-orange-600 hover:to-orange-700 disabled:opacity-50 transition-all shadow-lg shadow-orange-500/20"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Yaratilmoqda...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Exam yaratish
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}