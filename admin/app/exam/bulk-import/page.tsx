"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

// Shablonlar
const TEMPLATES = {
  reading: {
    exam: {
      code: "reading_b1_mock_01",
      title: "Reading Practice B1 - Technology",
      description: "This is a reading practice test for B1 level students.",
      exam_type: "reading",
      cefr_level: "B1",
      time_limit_sec: 1200,
      is_published: false,
    },
    blocks: [
      {
        block_type: "reading",
        title: "Part 1: Main Ideas",
        passage_text: `Technology has changed the way we communicate. In the past, people wrote letters and waited weeks for a reply. Today, we can send messages instantly using smartphones and social media.

However, this rapid communication has some drawbacks. Many people spend too much time on their phones and less time face-to-face with family and friends. Some experts believe that technology is making us more isolated, not more connected.

Despite these concerns, technology continues to evolve. New apps and devices are created every day, promising to make our lives easier and more efficient. The key is to use technology wisely and maintain a balance between digital and real-world interactions.`,
        order: 1,
        time_limit_sec: 600,
        items: [
          {
            item_type: "reading_question",
            title: "Question 1",
            question_text: "What is the main idea of the passage?",
            max_score: 1.0,
            order: 1,
            options: [
              { text: "Technology is bad for society.", is_correct: false, order: 1 },
              { text: "Technology changed communication but has drawbacks.", is_correct: true, order: 2 },
              { text: "People don't use phones anymore.", is_correct: false, order: 3 },
              { text: "Letters are better than emails.", is_correct: false, order: 4 },
            ],
          },
          {
            item_type: "reading_question",
            title: "Question 2",
            question_text: "According to the passage, what is a negative effect of technology?",
            max_score: 1.0,
            order: 2,
            options: [
              { text: "It makes communication slower.", is_correct: false, order: 1 },
              { text: "It reduces face-to-face interaction.", is_correct: true, order: 2 },
              { text: "It costs too much money.", is_correct: false, order: 3 },
              { text: "It doesn't work well.", is_correct: false, order: 4 },
            ],
          },
        ],
      },
    ],
  },
  full: {
    exam: {
      code: "full_exam_b1_mock_01",
      title: "Full Exam B1 - Practice Test 1",
      description: "Complete English exam with all 4 skills.",
      exam_type: "full",
      cefr_level: "B1",
      time_limit_sec: 7200,
      is_published: false,
    },
    blocks: [
      {
        block_type: "listening",
        title: "🎧 Listening Section",
        order: 1,
        time_limit_sec: 1800,
        items: [
          {
            item_type: "listening_question",
            title: "Listening Question 1",
            question_text: "What is the speaker talking about?",
            audio_url: "/media/exam/audio/sample.mp3",
            max_score: 1.0,
            order: 1,
            options: [
              { text: "Weather", is_correct: false, order: 1 },
              { text: "Travel", is_correct: true, order: 2 },
              { text: "Food", is_correct: false, order: 3 },
              { text: "Sports", is_correct: false, order: 4 },
            ],
          },
        ],
      },
      {
        block_type: "reading",
        title: "📖 Reading Section",
        passage_text: "Sample reading passage here...",
        order: 2,
        time_limit_sec: 1800,
        items: [
          {
            item_type: "reading_question",
            title: "Reading Question 1",
            question_text: "What is the main topic?",
            max_score: 1.0,
            order: 1,
            options: [
              { text: "Option A", is_correct: true, order: 1 },
              { text: "Option B", is_correct: false, order: 2 },
              { text: "Option C", is_correct: false, order: 3 },
              { text: "Option D", is_correct: false, order: 4 },
            ],
          },
        ],
      },
      {
        block_type: "writing",
        title: "✍️ Writing Section",
        order: 3,
        time_limit_sec: 1800,
        items: [
          {
            item_type: "writing_task",
            title: "Writing Task 1",
            question_text: "Write an email to your friend about your last holiday. Write 80-120 words.",
            min_words: 80,
            max_words: 120,
            max_score: 1.0,
            order: 1,
          },
        ],
      },
      {
        block_type: "speaking",
        title: "🎤 Speaking Section",
        order: 4,
        time_limit_sec: 1800,
        items: [
          {
            item_type: "speaking_task",
            title: "Speaking Task 1",
            question_text: "Describe your favourite teacher. You should say: who they are, what they teach, why you like them.",
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

export default function BulkImportPage() {
  const router = useRouter();
  const { token } = useAuth();
  const [jsonInput, setJsonInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  function loadTemplate(type: "reading" | "full") {
    setJsonInput(JSON.stringify(TEMPLATES[type], null, 2));
    setError("");
    setSuccess("");
  }

  function formatJSON() {
    try {
      const parsed = JSON.parse(jsonInput);
      setJsonInput(JSON.stringify(parsed, null, 2));
      setError("");
    } catch (e) {
      setError("❌ Noto'g'ri JSON formati");
    }
  }

  async function handleImport() {
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      // JSON validatsiya
      const payload = JSON.parse(jsonInput);

      const res = await fetch(`${API_URL}/api/v2/exam/admin/bulk-import`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `HTTP ${res.status}`);
      }

      const result = await res.json();
      setSuccess(
        `✅ ${result.message}\n\n` +
        `📊 Statistika:\n` +
        `• Blocks: ${result.stats.blocks_created}\n` +
        `• Items: ${result.stats.items_created}\n` +
        `• Options: ${result.stats.options_created}\n\n` +
        `Exam ID: ${result.exam_id}`
      );

      // 3 soniyadan keyin exam sahifasiga yo'naltirish
      setTimeout(() => {
        router.push(`/exam/exams/${result.exam_id}`);
      }, 3000);

    } catch (err) {
      setError(err instanceof Error ? err.message : "Import xatosi");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <button onClick={() => router.push("/exam/exams")} className="text-blue-600 mb-4 hover:underline">
        ← Examlarga qaytish
      </button>

      <h1 className="text-3xl font-bold mb-2">📥 JSON Bulk Import</h1>
      <p className="text-gray-600 mb-6">
        Tayyor JSON formatda toliq exam (exam + blocks + items + options) yuklang
      </p>

      {/* Shablon tugmalari */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">📋 Tayyor shablonlar</h2>
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => loadTemplate("reading")}
            className="bg-green-50 border-2 border-green-200 rounded-lg p-4 hover:bg-green-100 transition-colors text-left"
          >
            <div className="text-2xl mb-2">📖</div>
            <div className="font-bold text-green-900">Reading Exam</div>
            <div className="text-sm text-green-700 mt-1">
              1 block 2 savol passage bilan
            </div>
          </button>

          <button
            onClick={() => loadTemplate("full")}
            className="bg-purple-50 border-2 border-purple-200 rounded-lg p-4 hover:bg-purple-100 transition-colors text-left"
          >
            <div className="text-2xl mb-2">🎯</div>
            <div className="font-bold text-purple-900">Full Exam</div>
            <div className="text-sm text-purple-700 mt-1">
              4 block (Listening Reading Writing Speaking)
            </div>
          </button>
        </div>
      </div>

      {/* JSON Editor */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">📝 JSON kodni kiriting</h2>
          <button
            onClick={formatJSON}
            className="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg text-sm font-medium"
          >
            🎨 Formatlash
          </button>
        </div>

        <textarea
          value={jsonInput}
          onChange={(e) => setJsonInput(e.target.value)}
          placeholder="JSON kodni shu yerga joylashtiring..."
          rows={20}
          className="w-full border border-gray-300 rounded-lg px-4 py-3 font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />

        <div className="flex gap-3 mt-4">
          <button
            onClick={handleImport}
            disabled={loading || !jsonInput.trim()}
            className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold"
          >
            {loading ? "⏳ Yuklanmoqda..." : "🚀 Import qilish"}
          </button>
        </div>
      </div>

      {/* Natija */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg mb-4">
          <div className="font-bold mb-2">❌ Xatolik</div>
          <pre className="text-sm whitespace-pre-wrap">{error}</pre>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-800 p-4 rounded-lg">
          <div className="font-bold mb-2">✅ Muvaffaqiyatli!</div>
          <pre className="text-sm whitespace-pre-wrap">{success}</pre>
        </div>
      )}

      {/* Yordam */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-bold text-blue-900 mb-3">💡 Qanday ishlatish?</h3>
        <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800">
          <li>Yuqoridagi shablonlardan birini tanlang (Reading yoki Full Exam)</li>
          <li>JSON kodni oz malumotlaringiz bilan toldiring</li>
          <li>Formatlash tugmasini bosib, JSON ni chiroyli krinishga keltiring</li>
          <li>Import qilish tugmasini bosing</li>
          <li>Exam avtomatik yaratiladi va exam sahifasiga yonaltirilasiz</li>
        </ol>

        <div className="mt-4 p-4 bg-white rounded border border-blue-300">
          <div className="font-semibold text-blue-900 mb-2">📌 Muhim eslatmalar:</div>
          <ul className="list-disc list-inside space-y-1 text-sm text-blue-800">
            <li><code>exam.code</code> — unikal bolishi kerak</li>
            <li><code>block_type</code> — faqat: listening, reading, writing, speaking</li>
            <li><code>item_type</code> — faqat: listening_question, reading_question, writing_task, speaking_task</li>
            <li><code>is_correct</code> — boolean (true/false)</li>
            <li>Writing va Speaking uchun <code>options</code> kerak emas</li>
          </ul>
        </div>
      </div>
    </div>
  );
}