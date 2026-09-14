'use client';

import { useState, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileJson,
  CheckCircle2,
  AlertCircle,
  X,
  ArrowLeft,
  Sparkles,
  FileQuestion,
  List,
  Check,
  ChevronRight,
  Loader2,
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

interface ValidationError {
  test_index?: number;
  question_index?: number;
  location: string;
  message: string;
}

interface PreviewResult {
  valid: boolean;
  tests_count: number;
  total_questions: number;
  total_options: number;
  errors: ValidationError[];
  warnings: string[];
}

interface ImportResult {
  success: boolean;
  tests_created?: number;
  questions_created?: number;
  options_created?: number;
  test_ids?: number[];
  errors?: string[];
}

const SAMPLE_JSON = JSON.stringify(
  {
    tests: [
      {
        title: 'Grammar Test - Present Tenses',
        description: 'Test your knowledge of present simple and present continuous',
        category: 'Grammar',
        difficulty: 'B1',
        time_limit_min: 15,
        is_published: false,
        questions: [
          {
            question_text: 'She ___ to school every day.',
            question_type: 'single_choice',
            points: 1,
            order: 1,
            explanation: 'Present Simple is used for habits and routines.',
            options: [
              { text: 'go', is_correct: false, order: 1 },
              { text: 'goes', is_correct: true, order: 2 },
              { text: 'going', is_correct: false, order: 3 },
              { text: 'gone', is_correct: false, order: 4 },
            ],
          },
          {
            question_text: 'Which sentence is correct?',
            question_type: 'single_choice',
            points: 1,
            order: 2,
            options: [
              { text: 'I am work now.', is_correct: false, order: 1 },
              { text: 'I am working now.', is_correct: true, order: 2 },
              { text: 'I working now.', is_correct: false, order: 3 },
            ],
          },
        ],
      },
    ],
  },
  null,
  2
);

export default function TestsImportPage() {
  const router = useRouter();
  const { token } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [jsonInput, setJsonInput] = useState('');
  const [preview, setPreview] = useState<PreviewResult | null>(null);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFileUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
      setError('Faqat .json fayllar qabul qilinadi');
      return;
    }

    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (ev) => {
      setJsonInput(ev.target?.result as string);
      setPreview(null);
      setResult(null);
      setError('');
    };
    reader.readAsText(file);
  }, []);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
      setError('Faqat .json fayllar qabul qilinadi');
      return;
    }

    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (ev) => {
      setJsonInput(ev.target?.result as string);
      setPreview(null);
      setResult(null);
      setError('');
    };
    reader.readAsText(file);
  };

  const loadSample = () => {
    setJsonInput(SAMPLE_JSON);
    setFileName(null);
    setPreview(null);
    setResult(null);
    setError('');
    toast.success('Namuna JSON yuklandi');
  };

  const clearAll = () => {
    setJsonInput('');
    setFileName(null);
    setPreview(null);
    setResult(null);
    setError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handlePreview = async () => {
    setLoading(true);
    setError('');
    setPreview(null);
    setResult(null);

    try {
      const parsed = JSON.parse(jsonInput);

      const res = await fetch(`${API_URL}/api/tests/import/json/preview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(parsed),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(
          errData?.detail?.message || errData?.detail || `HTTP ${res.status}`
        );
      }

      const data: PreviewResult = await res.json();
      setPreview(data);

      if (data.valid) {
        toast.success('Validatsiya muvaffaqiyatli!');
      } else {
        toast.error(`${data.errors.length} ta xato topildi`);
      }
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError('JSON format notogri. Valid JSON kiriting.');
      } else {
        setError(err instanceof Error ? err.message : 'Xatolik yuz berdi');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!preview?.valid) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const parsed = JSON.parse(jsonInput);

      const res = await fetch(`${API_URL}/api/tests/import/json/confirm`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(parsed),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail?.message || `HTTP ${res.status}`);
      }

      const data: ImportResult = await res.json();
      setResult(data);

      if (data.success) {
        setPreview(null);
        toast.success(`${data.tests_created} ta test saqlandi!`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Saqlashda xato');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push('/tests')}
            className="p-2 text-slate-600 hover:bg-slate-100 rounded-xl transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-slate-900">
              Test Import
            </h1>
            <p className="text-sm md:text-base text-slate-600 mt-0.5">
              JSON fayl orqali testlarni ommaviy yuklang
            </p>
          </div>
        </div>

        <button
          onClick={loadSample}
          className="flex items-center gap-2 px-4 py-2.5 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 transition font-medium text-sm"
        >
          <Sparkles className="w-4 h-4" />
          Namuna JSON
        </button>
      </div>

      {/* Steps indicator */}
      <div className="hidden md:flex items-center gap-4 p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
        <div
          className={`flex items-center gap-2 ${
            jsonInput && !result ? 'text-orange-600' : 'text-slate-400'
          }`}
        >
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
              jsonInput && !result
                ? 'bg-orange-100 text-orange-600'
                : 'bg-slate-100 text-slate-400'
            }`}
          >
            1
          </div>
          <span className="text-sm font-medium">Fayl yuklash</span>
        </div>
        <ChevronRight className="w-4 h-4 text-slate-300" />
        <div
          className={`flex items-center gap-2 ${
            preview?.valid ? 'text-orange-600' : 'text-slate-400'
          }`}
        >
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
              preview?.valid
                ? 'bg-orange-100 text-orange-600'
                : 'bg-slate-100 text-slate-400'
            }`}
          >
            2
          </div>
          <span className="text-sm font-medium">Tekshirish</span>
        </div>
        <ChevronRight className="w-4 h-4 text-slate-300" />
        <div
          className={`flex items-center gap-2 ${
            result?.success ? 'text-emerald-600' : 'text-slate-400'
          }`}
        >
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
              result?.success
                ? 'bg-emerald-100 text-emerald-600'
                : 'bg-slate-100 text-slate-400'
            }`}
          >
            3
          </div>
          <span className="text-sm font-medium">Saqlash</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Upload + Editor */}
        <div className="space-y-4">
          {/* Upload area */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
          >
            <div className="p-5 border-b border-slate-100">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Upload className="w-5 h-5 text-orange-500" />
                Fayl yuklash
              </h2>
            </div>

            <div className="p-5">
              <label
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-xl cursor-pointer transition-all ${
                  isDragging
                    ? 'border-orange-500 bg-orange-50'
                    : 'border-slate-300 hover:border-orange-400 hover:bg-slate-50'
                }`}
              >
                <div className="flex flex-col items-center gap-2 text-slate-500">
                  <div
                    className={`w-12 h-12 rounded-xl flex items-center justify-center transition ${
                      isDragging ? 'bg-orange-100' : 'bg-slate-100'
                    }`}
                  >
                    <FileJson
                      className={`w-6 h-6 ${
                        isDragging ? 'text-orange-500' : 'text-slate-400'
                      }`}
                    />
                  </div>
                  <span className="text-sm font-medium text-slate-700">
                    {isDragging
                      ? 'Shu yerga qoying...'
                      : fileName || 'JSON faylni tanlang yoki tashlang'}
                  </span>
                  <span className="text-xs text-slate-400">.json format</span>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".json"
                  onChange={handleFileUpload}
                  className="sr-only"
                />
              </label>

              {fileName && (
                <div className="mt-3 flex items-center gap-2 p-3 bg-orange-50 border border-orange-200 rounded-xl">
                  <FileJson className="w-4 h-4 text-orange-600" />
                  <span className="text-sm text-orange-800 flex-1 truncate">
                    {fileName}
                  </span>
                  <button
                    onClick={clearAll}
                    className="p-1 text-orange-400 hover:text-orange-600 rounded transition"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </motion.div>

          {/* JSON Editor */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
          >
            <div className="p-5 border-b border-slate-100 flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <FileJson className="w-5 h-5 text-orange-500" />
                JSON malumotlar
              </h2>
              {jsonInput && (
                <button
                  onClick={clearAll}
                  className="text-xs text-slate-500 hover:text-slate-700 font-medium"
                >
                  Tozalash
                </button>
              )}
            </div>

            <div className="p-5">
              <textarea
                value={jsonInput}
                onChange={(e) => {
                  setJsonInput(e.target.value);
                  setPreview(null);
                  setResult(null);
                  setFileName(null);
                }}
                placeholder='{"tests": [...]}'
                rows={12}
                className="w-full font-mono text-xs border border-slate-200 rounded-xl bg-slate-50 p-4 focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 resize-y transition-all"
              />

              <button
                onClick={handlePreview}
                disabled={!jsonInput.trim() || loading}
                className="w-full mt-4 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl font-semibold hover:from-orange-600 hover:to-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-orange-500/20 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Tekshirilmoqda...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    Tekshirish (Preview)
                  </>
                )}
              </button>
            </div>
          </motion.div>
        </div>

        {/* Right: Preview / Result */}
        <div className="space-y-4">
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
                  <p className="text-sm font-medium text-red-800">Xatolik</p>
                  <p className="text-sm text-red-600 mt-1">{error}</p>
                </div>
                <button
                  onClick={() => setError('')}
                  className="p-1 text-red-400 hover:text-red-600 rounded transition"
                >
                  <X className="w-4 h-4" />
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Preview */}
          <AnimatePresence>
            {preview && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`rounded-2xl border shadow-sm overflow-hidden ${
                  preview.valid
                    ? 'bg-emerald-50 border-emerald-200'
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <div
                  className={`p-5 border-b ${
                    preview.valid ? 'border-emerald-200' : 'border-red-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                        preview.valid ? 'bg-emerald-100' : 'bg-red-100'
                      }`}
                    >
                      {preview.valid ? (
                        <CheckCircle2 className="w-6 h-6 text-emerald-600" />
                      ) : (
                        <AlertCircle className="w-6 h-6 text-red-600" />
                      )}
                    </div>
                    <div>
                      <h2
                        className={`text-lg font-bold ${
                          preview.valid ? 'text-emerald-900' : 'text-red-900'
                        }`}
                      >
                        {preview.valid
                          ? 'Validatsiya muvaffaqiyatli!'
                          : 'Validatsiya xatolari bor'}
                      </h2>
                      <p
                        className={`text-sm ${
                          preview.valid ? 'text-emerald-700' : 'text-red-700'
                        }`}
                      >
                        {preview.valid
                          ? 'Testlarni saqlashingiz mumkin'
                          : `${preview.errors.length} ta xato topildi`}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-5">
                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-3 mb-4">
                    <div className="bg-white/70 rounded-xl p-3 text-center">
                      <FileQuestion
                        className={`w-5 h-5 mx-auto mb-1 ${
                          preview.valid ? 'text-emerald-600' : 'text-red-600'
                        }`}
                      />
                      <p className="text-2xl font-bold text-slate-900">
                        {preview.tests_count}
                      </p>
                      <p className="text-xs text-slate-500">Testlar</p>
                    </div>
                    <div className="bg-white/70 rounded-xl p-3 text-center">
                      <List
                        className={`w-5 h-5 mx-auto mb-1 ${
                          preview.valid ? 'text-emerald-600' : 'text-red-600'
                        }`}
                      />
                      <p className="text-2xl font-bold text-slate-900">
                        {preview.total_questions}
                      </p>
                      <p className="text-xs text-slate-500">Savollar</p>
                    </div>
                    <div className="bg-white/70 rounded-xl p-3 text-center">
                      <Check
                        className={`w-5 h-5 mx-auto mb-1 ${
                          preview.valid ? 'text-emerald-600' : 'text-red-600'
                        }`}
                      />
                      <p className="text-2xl font-bold text-slate-900">
                        {preview.total_options}
                      </p>
                      <p className="text-xs text-slate-500">Variantlar</p>
                    </div>
                  </div>

                  {/* Errors */}
                  {preview.errors.length > 0 && (
                    <div className="mb-4">
                      <h3 className="text-sm font-bold text-red-700 mb-2 flex items-center gap-1.5">
                        <AlertCircle className="w-4 h-4" />
                        Xatolar ({preview.errors.length})
                      </h3>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {preview.errors.map((err, idx) => (
                          <div
                            key={idx}
                            className="bg-white/70 rounded-lg p-2.5 text-xs"
                          >
                            <span className="font-mono text-[10px] bg-red-100 text-red-700 px-1.5 py-0.5 rounded mr-2">
                              {err.location}
                            </span>
                            <span className="text-red-800">{err.message}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Warnings */}
                  {preview.warnings.length > 0 && (
                    <div className="mb-4">
                      <h3 className="text-sm font-bold text-amber-700 mb-2">
                        Ogohlantirishlar ({preview.warnings.length})
                      </h3>
                      <div className="space-y-1.5 max-h-32 overflow-y-auto">
                        {preview.warnings.map((warn, idx) => (
                          <div
                            key={idx}
                            className="bg-amber-50/70 rounded-lg p-2 text-xs text-amber-800"
                          >
                            {warn}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Confirm button */}
                  {preview.valid && (
                    <button
                      onClick={handleConfirm}
                      disabled={loading}
                      className="w-full py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl font-semibold hover:from-emerald-600 hover:to-emerald-700 disabled:opacity-50 transition-all shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Saqlanmoqda...
                        </>
                      ) : (
                        <>
                          <Check className="w-4 h-4" />
                          Tasdiqlash va Saqlash
                        </>
                      )}
                    </button>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Success */}
          <AnimatePresence>
            {result?.success && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl shadow-xl overflow-hidden text-white"
              >
                <div className="p-6">
                  <div className="flex items-center gap-4 mb-5">
                    <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                      <Sparkles className="w-7 h-7" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold">Import muvaffaqiyatli!</h2>
                      <p className="text-sm text-white/80">
                        Testlar bazaga saqlandi
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-3 mb-6">
                    <div className="bg-white/15 backdrop-blur-sm rounded-xl p-3 text-center">
                      <p className="text-2xl font-bold">{result.tests_created}</p>
                      <p className="text-xs text-white/80">Testlar</p>
                    </div>
                    <div className="bg-white/15 backdrop-blur-sm rounded-xl p-3 text-center">
                      <p className="text-2xl font-bold">
                        {result.questions_created}
                      </p>
                      <p className="text-xs text-white/80">Savollar</p>
                    </div>
                    <div className="bg-white/15 backdrop-blur-sm rounded-xl p-3 text-center">
                      <p className="text-2xl font-bold">
                        {result.options_created}
                      </p>
                      <p className="text-xs text-white/80">Variantlar</p>
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={() => router.push('/tests')}
                      className="flex-1 py-3 bg-white text-emerald-700 rounded-xl font-semibold hover:bg-white/90 transition-all flex items-center justify-center gap-2"
                    >
                      <FileQuestion className="w-4 h-4" />
                      Testlar royxati
                    </button>
                    <button
                      onClick={clearAll}
                      className="flex-1 py-3 bg-white/20 backdrop-blur-sm text-white rounded-xl font-semibold hover:bg-white/30 transition-all flex items-center justify-center gap-2"
                    >
                      <Upload className="w-4 h-4" />
                      Yangi import
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Info card */}
          {!preview && !result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5"
            >
              <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-orange-500" />
                JSON formati
              </h3>
              <div className="space-y-2 text-xs text-slate-600">
                <p>• Har bir testda <code className="bg-slate-100 px-1.5 py-0.5 rounded">title</code> va <code className="bg-slate-100 px-1.5 py-0.5 rounded">questions</code> bolishi kerak</p>
                <p>• Har bir savolda kamida 2 ta variant bolishi kerak</p>
                <p>• Kamida bitta variant <code className="bg-slate-100 px-1.5 py-0.5 rounded">is_correct: true</code> bolishi shart</p>
                <p>• <code className="bg-slate-100 px-1.5 py-0.5 rounded">difficulty</code>: A1, A2, B1, B2, C1, C2</p>
              </div>

              <button
                onClick={loadSample}
                className="w-full mt-4 py-2.5 bg-slate-100 text-slate-700 rounded-xl text-sm font-medium hover:bg-slate-200 transition-all flex items-center justify-center gap-2"
              >
                <FileJson className="w-4 h-4" />
                Namuna yuklash
              </button>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}