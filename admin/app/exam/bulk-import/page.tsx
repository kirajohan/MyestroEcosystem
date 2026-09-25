'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft,
  FileJson,
  Sparkles,
  Wand2,
  Upload,
  CheckCircle2,
  AlertCircle,
  BookOpen,
  Target,
  Copy,
  Info,
  Loader2,
  Clipboard,
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://myestroeco-backend-production.up.railway.app';

const TEMPLATES = {
  reading: {
    exam: {
      code: 'reading_b1_mock_01',
      title: 'Reading Practice B1 - Technology',
      description: 'This is a reading practice test for B1 level students.',
      exam_type: 'reading',
      cefr_level: 'B1',
      time_limit_sec: 1200,
      is_published: false,
    },
    blocks: [
      {
        block_type: 'reading',
        title: 'Part 1: Main Ideas',
        passage_text:
          'Technology has changed the way we communicate. In the past, people wrote letters and waited weeks for a reply. Today, we can send messages instantly using smartphones and social media.\n\nHowever, this rapid communication has some drawbacks. Many people spend too much time on their phones and less time face-to-face with family and friends.\n\nDespite these concerns, technology continues to evolve. New apps and devices are created every day, promising to make our lives easier and more efficient.',
        order: 1,
        time_limit_sec: 600,
        items: [
          {
            item_type: 'reading_question',
            title: 'Question 1',
            question_text: 'What is the main idea of the passage?',
            max_score: 1.0,
            order: 1,
            options: [
              { text: 'Technology is bad for society.', is_correct: false, order: 1 },
              {
                text: 'Technology changed communication but has drawbacks.',
                is_correct: true,
                order: 2,
              },
              { text: 'People do not use phones anymore.', is_correct: false, order: 3 },
              { text: 'Letters are better than emails.', is_correct: false, order: 4 },
            ],
          },
          {
            item_type: 'reading_question',
            title: 'Question 2',
            question_text: 'According to the passage, what is a negative effect of technology?',
            max_score: 1.0,
            order: 2,
            options: [
              { text: 'It makes communication slower.', is_correct: false, order: 1 },
              { text: 'It reduces face-to-face interaction.', is_correct: true, order: 2 },
              { text: 'It costs too much money.', is_correct: false, order: 3 },
              { text: 'It does not work well.', is_correct: false, order: 4 },
            ],
          },
        ],
      },
    ],
  },
  full: {
    exam: {
      code: 'full_exam_b1_mock_01',
      title: 'Full Exam B1 - Practice Test 1',
      description: 'Complete English exam with all 4 skills.',
      exam_type: 'full',
      cefr_level: 'B1',
      time_limit_sec: 7200,
      is_published: false,
    },
    blocks: [
      {
        block_type: 'listening',
        title: 'Listening Section',
        order: 1,
        time_limit_sec: 1800,
        items: [
          {
            item_type: 'listening_question',
            title: 'Listening Question 1',
            question_text: 'What is the speaker talking about?',
            audio_url: '/media/exam/audio/sample.mp3',
            max_score: 1.0,
            order: 1,
            options: [
              { text: 'Weather', is_correct: false, order: 1 },
              { text: 'Travel', is_correct: true, order: 2 },
              { text: 'Food', is_correct: false, order: 3 },
              { text: 'Sports', is_correct: false, order: 4 },
            ],
          },
        ],
      },
      {
        block_type: 'reading',
        title: 'Reading Section',
        passage_text: 'Sample reading passage here...',
        order: 2,
        time_limit_sec: 1800,
        items: [
          {
            item_type: 'reading_question',
            title: 'Reading Question 1',
            question_text: 'What is the main topic?',
            max_score: 1.0,
            order: 1,
            options: [
              { text: 'Option A', is_correct: true, order: 1 },
              { text: 'Option B', is_correct: false, order: 2 },
              { text: 'Option C', is_correct: false, order: 3 },
              { text: 'Option D', is_correct: false, order: 4 },
            ],
          },
        ],
      },
      {
        block_type: 'writing',
        title: 'Writing Section',
        order: 3,
        time_limit_sec: 1800,
        items: [
          {
            item_type: 'writing_task',
            title: 'Writing Task 1',
            question_text: 'Write an email to your friend about your last holiday. Write 80-120 words.',
            min_words: 80,
            max_words: 120,
            max_score: 1.0,
            order: 1,
          },
        ],
      },
      {
        block_type: 'speaking',
        title: 'Speaking Section',
        order: 4,
        time_limit_sec: 1800,
        items: [
          {
            item_type: 'speaking_task',
            title: 'Speaking Task 1',
            question_text:
              'Describe your favourite teacher. You should say: who they are, what they teach, why you like them.',
            preparation_time_sec: 30,
            answer_time_sec: 60,
            max_score: 1.0,
            order: 1,
          },
        ],
      },
    ],
  },
};

interface ImportResult {
  exam_id: number;
  message: string;
  stats: {
    blocks_created: number;
    items_created: number;
    options_created: number;
  };
}

export default function BulkImportPage() {
  const router = useRouter();
  const { token } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [jsonInput, setJsonInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState<ImportResult | null>(null);

  function loadTemplate(type: 'reading' | 'full') {
    setJsonInput(JSON.stringify(TEMPLATES[type], null, 2));
    setError('');
    setSuccess(null);
    toast.success(`${type === 'reading' ? 'Reading' : 'Full Exam'} shabloni yuklandi`);
  }

  function formatJSON() {
    try {
      const parsed = JSON.parse(jsonInput);
      setJsonInput(JSON.stringify(parsed, null, 2));
      setError('');
      toast.success('JSON formatlandi');
    } catch (e) {
      setError('Noto\'g\'ri JSON formati');
      toast.error('JSON formati notogri');
    }
  }

  function copyToClipboard() {
    navigator.clipboard.writeText(jsonInput);
    toast.success('Clipboardga nusxalandi');
  }

  function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (ev) => {
      setJsonInput(ev.target?.result as string);
      setError('');
      setSuccess(null);
      toast.success(`${file.name} yuklandi`);
    };
    reader.readAsText(file);
  }

  async function handleImport() {
    setError('');
    setSuccess(null);
    setLoading(true);

    try {
      const payload = JSON.parse(jsonInput);

      const res = await fetch(`${API_URL}/api/v2/exam/admin/bulk-import`, {
        method: 'POST',
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

      const result: ImportResult = await res.json();
      setSuccess(result);
      toast.success(`Import muvaffaqiyatli! ${result.stats.items_created} ta savol yaratildi`);

      setTimeout(() => {
        router.push(`/exam/exams/${result.exam_id}`);
      }, 3000);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Import xatosi';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  const isValidJSON = (() => {
    try {
      JSON.parse(jsonInput);
      return jsonInput.trim().length > 0;
    } catch {
      return false;
    }
  })();

  return (
    <div className="space-y-6">
      {/* Back button + Header */}
      <div className="flex flex-col gap-2">
        <button
          onClick={() => router.push('/exam/exams')}
          className="flex items-center gap-2 text-sm text-slate-600 hover:text-orange-600 transition-colors w-fit"
        >
          <ArrowLeft className="w-4 h-4" />
          Examlarga qaytish
        </button>

        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">JSON Bulk Import</h1>
          <p className="text-sm md:text-base text-slate-600 mt-1">
            Tayyor JSON formatda toliq exam yuklang (exam + blocks + items + options)
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Templates + Info */}
        <div className="space-y-4">
          {/* Templates */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
          >
            <div className="p-5 border-b border-slate-100">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-orange-500" />
                Tayyor shablonlar
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">Bir bosishda yuklang</p>
            </div>

            <div className="p-4 space-y-3">
              <button
                onClick={() => loadTemplate('reading')}
                className="w-full p-4 bg-emerald-50 border-2 border-emerald-200 rounded-xl hover:bg-emerald-100 hover:border-emerald-300 transition-all text-left group"
              >
                <div className="flex items-start gap-3">
                  <div className="w-11 h-11 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-sm shadow-emerald-500/20 flex-shrink-0">
                    <BookOpen className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-emerald-900">Reading Exam</p>
                    <p className="text-xs text-emerald-700 mt-0.5">
                      1 block, 2 savol, passage bilan
                    </p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => loadTemplate('full')}
                className="w-full p-4 bg-purple-50 border-2 border-purple-200 rounded-xl hover:bg-purple-100 hover:border-purple-300 transition-all text-left group"
              >
                <div className="flex items-start gap-3">
                  <div className="w-11 h-11 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center shadow-sm shadow-purple-500/20 flex-shrink-0">
                    <Target className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-purple-900">Full Exam</p>
                    <p className="text-xs text-purple-700 mt-0.5">
                      4 block (L, R, W, S)
                    </p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => fileInputRef.current?.click()}
                className="w-full p-4 bg-slate-50 border-2 border-dashed border-slate-300 rounded-xl hover:bg-slate-100 hover:border-slate-400 transition-all text-left"
              >
                <div className="flex items-start gap-3">
                  <div className="w-11 h-11 bg-white border border-slate-200 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Upload className="w-5 h-5 text-slate-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-bold text-slate-900">Fayldan yuklash</p>
                    <p className="text-xs text-slate-500 mt-0.5">.json fayl tanlang</p>
                  </div>
                </div>
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".json"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
          </motion.div>

          {/* Info */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-5"
          >
            <div className="flex items-center gap-2 mb-3">
              <Info className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-blue-900">Muhim eslatmalar</h3>
            </div>
            <ul className="space-y-2 text-xs text-blue-800">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold flex-shrink-0">•</span>
                <span>
                  <code className="bg-white px-1.5 py-0.5 rounded text-[10px] font-mono">exam.code</code>{' '}
                  unikal bolishi kerak
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold flex-shrink-0">•</span>
                <span>
                  <code className="bg-white px-1.5 py-0.5 rounded text-[10px] font-mono">block_type</code>:{' '}
                  listening, reading, writing, speaking
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold flex-shrink-0">•</span>
                <span>
                  <code className="bg-white px-1.5 py-0.5 rounded text-[10px] font-mono">item_type</code>:{' '}
                  listening_question, reading_question, writing_task, speaking_task
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold flex-shrink-0">•</span>
                <span>
                  <code className="bg-white px-1.5 py-0.5 rounded text-[10px] font-mono">is_correct</code> — boolean
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold flex-shrink-0">•</span>
                <span>Writing va Speaking uchun options kerak emas</span>
              </li>
            </ul>
          </motion.div>
        </div>

        {/* Right Column - Editor + Result */}
        <div className="lg:col-span-2 space-y-4">
          {/* JSON Editor */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
          >
            <div className="p-5 border-b border-slate-100 bg-slate-50">
              <div className="flex items-center justify-between mb-1">
                <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <FileJson className="w-5 h-5 text-orange-500" />
                  JSON kod
                </h2>
                <div className="flex items-center gap-1">
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold ${
                      isValidJSON
                        ? 'bg-emerald-100 text-emerald-700'
                        : jsonInput.trim()
                        ? 'bg-red-100 text-red-700'
                        : 'bg-slate-100 text-slate-500'
                    }`}
                  >
                    {isValidJSON ? (
                      <>
                        <CheckCircle2 className="w-3 h-3" />
                        Valid
                      </>
                    ) : jsonInput.trim() ? (
                      <>
                        <AlertCircle className="w-3 h-3" />
                        Invalid
                      </>
                    ) : (
                      'Bosh'
                    )}
                  </span>
                </div>
              </div>
              <p className="text-xs text-slate-500">
                Shablonni tanlang yoki oz JSON kodni kiriting
              </p>
            </div>

            <div className="p-4">
              <textarea
                value={jsonInput}
                onChange={(e) => {
                  setJsonInput(e.target.value);
                  setSuccess(null);
                }}
                placeholder='{"exam": {...}, "blocks": [...]}'
                rows={18}
                className="w-full font-mono text-xs border border-slate-200 rounded-xl bg-slate-50 p-4 focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all resize-y"
              />

              <div className="flex flex-wrap gap-2 mt-3">
                <button
                  onClick={formatJSON}
                  disabled={!jsonInput.trim()}
                  className="flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  <Wand2 className="w-3.5 h-3.5" />
                  Formatlash
                </button>
                <button
                  onClick={copyToClipboard}
                  disabled={!jsonInput.trim()}
                  className="flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  <Clipboard className="w-3.5 h-3.5" />
                  Nusxalash
                </button>
                <button
                  onClick={() => {
                    setJsonInput('');
                    setSuccess(null);
                    setError('');
                  }}
                  disabled={!jsonInput.trim()}
                  className="flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  Tozalash
                </button>

                <button
                  onClick={handleImport}
                  disabled={loading || !isValidJSON}
                  className="ml-auto flex items-center gap-1.5 px-5 py-2 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-lg text-xs font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-orange-500/20"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      Import...
                    </>
                  ) : (
                    <>
                      <Upload className="w-3.5 h-3.5" />
                      Import qilish
                    </>
                  )}
                </button>
              </div>
            </div>
          </motion.div>

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
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-red-800 mb-1">Xatolik</p>
                  <pre className="text-xs text-red-700 whitespace-pre-wrap font-mono">
                    {error}
                  </pre>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Success */}
          <AnimatePresence>
            {success && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl shadow-xl overflow-hidden text-white"
              >
                <div className="p-6">
                  <div className="flex items-start gap-4 mb-5">
                    <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center flex-shrink-0">
                      <CheckCircle2 className="w-7 h-7" />
                    </div>
                    <div className="flex-1">
                      <h2 className="text-xl font-bold">Import muvaffaqiyatli!</h2>
                      <p className="text-sm text-white/80 mt-0.5">{success.message}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3 mb-5">
                    <div className="bg-white/15 backdrop-blur-sm rounded-xl p-3 text-center">
                      <p className="text-2xl font-bold">{success.stats.blocks_created}</p>
                      <p className="text-xs text-white/80">Blocklar</p>
                    </div>
                    <div className="bg-white/15 backdrop-blur-sm rounded-xl p-3 text-center">
                      <p className="text-2xl font-bold">{success.stats.items_created}</p>
                      <p className="text-xs text-white/80">Savollar</p>
                    </div>
                    <div className="bg-white/15 backdrop-blur-sm rounded-xl p-3 text-center">
                      <p className="text-2xl font-bold">{success.stats.options_created}</p>
                      <p className="text-xs text-white/80">Variantlar</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 p-3 bg-white/10 backdrop-blur-sm rounded-xl">
                    <FileJson className="w-4 h-4" />
                    <span className="text-xs text-white/80">Exam ID:</span>
                    <span className="text-sm font-bold">{success.exam_id}</span>
                    <span className="ml-auto text-xs text-white/60">3 soniyada yonaltiriladi...</span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Steps */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
          >
            <div className="p-5 border-b border-slate-100">
              <h3 className="font-bold text-slate-900">Qanday ishlatish?</h3>
            </div>
            <div className="p-5 space-y-3">
              {[
                { num: 1, text: 'Yuqoridagi shablonlardan birini tanlang (Reading yoki Full Exam)' },
                { num: 2, text: 'JSON kodni oz malumotlaringiz bilan toldiring' },
                { num: 3, text: 'Formatlash tugmasini bosib, JSONni chiroyli korinishga keltiring' },
                { num: 4, text: 'Import qilish tugmasini bosing' },
                { num: 5, text: 'Exam avtomatik yaratiladi va exam sahifasiga yonaltirilasiz' },
              ].map((step) => (
                <div key={step.num} className="flex items-start gap-3">
                  <div className="w-7 h-7 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center text-white text-xs font-bold flex-shrink-0 shadow-sm shadow-orange-500/20">
                    {step.num}
                  </div>
                  <p className="text-sm text-slate-700 leading-relaxed pt-0.5">{step.text}</p>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}