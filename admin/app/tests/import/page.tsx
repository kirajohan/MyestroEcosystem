"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

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

// Namuna JSON
const SAMPLE_JSON = JSON.stringify({
  tests: [
    {
      title: "Grammar Test - Present Tenses",
      description: "Test your knowledge of present simple and present continuous",
      category: "Grammar",
      difficulty: "B1",
      time_limit_min: 15,
      is_published: false,
      questions: [
        {
          question_text: "She ___ to school every day.",
          question_type: "single_choice",
          points: 1,
          order: 1,
          explanation: "Present Simple is used for habits and routines.",
          options: [
            { text: "go", is_correct: false, order: 1 },
            { text: "goes", is_correct: true, order: 2 },
            { text: "going", is_correct: false, order: 3 },
            { text: "gone", is_correct: false, order: 4 }
          ]
        },
        {
          question_text: "Which sentence is correct?",
          question_type: "single_choice",
          points: 1,
          order: 2,
          options: [
            { text: "I am work now.", is_correct: false, order: 1 },
            { text: "I am working now.", is_correct: true, order: 2 },
            { text: "I working now.", is_correct: false, order: 3 }
          ]
        }
      ]
    }
  ]
}, null, 2);

export default function TestsImportPage() {
  const router = useRouter();
  const { token } = useAuth();

  const [jsonInput, setJsonInput] = useState("");
  const [preview, setPreview] = useState<PreviewResult | null>(null);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (ev) => {
      setJsonInput(ev.target?.result as string);
      setPreview(null);
      setResult(null);
      setError("");
    };
    reader.readAsText(file);
  }

  function loadSample() {
    setJsonInput(SAMPLE_JSON);
    setPreview(null);
    setResult(null);
    setError("");
  }

  async function handlePreview() {
    setLoading(true);
    setError("");
    setPreview(null);
    setResult(null);

    try {
      const parsed = JSON.parse(jsonInput);

      const res = await fetch(`${API_URL}/api/tests/import/json/preview`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(parsed),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail?.message || errData?.detail || `HTTP ${res.status}`);
      }

      const data: PreviewResult = await res.json();
      setPreview(data);
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError("JSON format noto'g'ri. Valid JSON kiriting.");
      } else {
        setError(err instanceof Error ? err.message : "Xatolik yuz berdi");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleConfirm() {
    if (!preview?.valid) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const parsed = JSON.parse(jsonInput);

      const res = await fetch(`${API_URL}/api/tests/import/json/confirm`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
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
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Saqlashda xato");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">📥 Test Import (JSON)</h1>
          <p className="text-sm text-slate-500 mt-1">
            JSON fayl orqali quiz va savollarni ommaviy yuklang
          </p>
        </div>
        <button
          onClick={() => router.push("/tests")}
          className="text-blue-600 hover:underline text-sm"
        >
          ← Tests royxatiga qaytish
        </button>
      </div>

      {/* Upload Area */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
        <label className="block cursor-pointer">
          <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center hover:border-blue-400 hover:bg-blue-50 transition-all">
            <div className="text-3xl mb-2">📄</div>
            <p className="font-medium text-slate-700">JSON faylni shu yerga tashlang</p>
            <p className="text-xs text-slate-500 mt-1">yoki bosib tanlang (.json)</p>
          </div>
          <input
            type="file"
            accept=".json"
            onChange={handleFileUpload}
            className="hidden"
          />
        </label>

        <button
          onClick={loadSample}
          className="px-4 py-2 text-sm bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
        >
          📋 Namuna JSON yuklash
        </button>

        <textarea
          value={jsonInput}
          onChange={(e) => {
            setJsonInput(e.target.value);
            setPreview(null);
            setResult(null);
          }}
          placeholder='JSON malumotni shu yerga joylashtiring...'
          rows={16}
          className="w-full font-mono text-sm border border-slate-300 rounded-lg p-4 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-y"
        />

        <button
          onClick={handlePreview}
          disabled={!jsonInput.trim() || loading}
          className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Tekshirilmoqda..." : "🔍 Tekshirish (Preview)"}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700">
          ❌ {error}
        </div>
      )}

      {/* Preview */}
      {preview && (
        <div className={`rounded-xl border p-6 space-y-4 ${
          preview.valid
            ? "bg-emerald-50 border-emerald-200"
            : "bg-red-50 border-red-200"
        }`}>
          <div className="flex items-center gap-3">
            <span className="text-3xl">{preview.valid ? "✅" : "❌"}</span>
            <div>
              <h2 className="text-lg font-bold">
                {preview.valid ? "Validatsiya muvaffaqiyatli!" : "Validatsiya xatolari bor"}
              </h2>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white/70 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold">{preview.tests_count}</div>
              <div className="text-xs uppercase tracking-wide opacity-70">Testlar</div>
            </div>
            <div className="bg-white/70 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold">{preview.total_questions}</div>
              <div className="text-xs uppercase tracking-wide opacity-70">Savollar</div>
            </div>
            <div className="bg-white/70 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold">{preview.total_options}</div>
              <div className="text-xs uppercase tracking-wide opacity-70">Variantlar</div>
            </div>
          </div>

          {preview.errors.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-bold text-red-700 text-sm">
                ❌ Xatolar ({preview.errors.length})
              </h3>
              {preview.errors.map((err, idx) => (
                <div key={idx} className="bg-white/70 rounded-lg p-3 text-sm">
                  <span className="font-mono text-xs bg-red-100 px-2 py-0.5 rounded mr-2">
                    {err.location}
                  </span>
                  {err.message}
                </div>
              ))}
            </div>
          )}

          {preview.warnings.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-bold text-amber-700 text-sm">
                ⚠️ Ogohlantirishlar ({preview.warnings.length})
              </h3>
              {preview.warnings.map((warn, idx) => (
                <div key={idx} className="bg-white/70 rounded-lg p-3 text-sm text-amber-800">
                  {warn}
                </div>
              ))}
            </div>
          )}

          {preview.valid && (
            <button
              onClick={handleConfirm}
              disabled={loading}
              className="w-full py-3 bg-emerald-600 text-white rounded-lg font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors"
            >
              {loading ? "Saqlanmoqda..." : "✅ Tasdiqlash va Saqlash"}
            </button>
          )}
        </div>
      )}

      {/* Success */}
      {result?.success && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-3">
            <span className="text-4xl">🎉</span>
            <div>
              <h2 className="text-xl font-bold text-emerald-900">Import muvaffaqiyatli!</h2>
              <p className="text-sm text-emerald-700">Testlar bazaga saqlandi</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="bg-white/70 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-emerald-700">{result.tests_created}</div>
              <div className="text-xs uppercase tracking-wide text-emerald-600">Testlar</div>
            </div>
            <div className="bg-white/70 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-emerald-700">{result.questions_created}</div>
              <div className="text-xs uppercase tracking-wide text-emerald-600">Savollar</div>
            </div>
            <div className="bg-white/70 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-emerald-700">{result.options_created}</div>
              <div className="text-xs uppercase tracking-wide text-emerald-600">Variantlar</div>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => router.push("/tests")}
              className="flex-1 py-3 bg-emerald-600 text-white rounded-lg font-semibold hover:bg-emerald-700 transition-colors"
            >
              📝 Tests royxatiga otish
            </button>
            <button
              onClick={() => {
                setJsonInput("");
                setResult(null);
              }}
              className="flex-1 py-3 border border-emerald-300 text-emerald-700 rounded-lg font-semibold hover:bg-emerald-50 transition-colors"
            >
              🔄 Yangi import
            </button>
          </div>
        </div>
      )}
    </div>
  );
}