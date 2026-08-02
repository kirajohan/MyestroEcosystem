'use client';

import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { Plus, Pencil, Trash2, FileQuestion, ChevronDown, ChevronUp, X, CheckCircle2, AlertCircle } from 'lucide-react';

interface Test {
  id: number;
  title: string;
  description: string | null;
  cefr_level: string;
  status: string;
  total_duration: number;
  passing_score: number | null;
  max_score: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface Question {
  id: number;
  question_text: string;
  question_type: string;
  options: { label: string; is_correct: boolean }[] | null;
  correct_answer: string;
  explanation: string | null;
  points: number;
  difficulty: string;
  order_index: number;
}

const CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

export default function TestsPage() {
  const [tests, setTests] = useState<Test[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create/Edit modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTest, setEditingTest] = useState<Test | null>(null);
  const [formTitle, setFormTitle] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [formLevel, setFormLevel] = useState('A1');
  const [formDuration, setFormDuration] = useState(30);
  const [formPassingScore, setFormPassingScore] = useState('60');
  const [formSaving, setFormSaving] = useState(false);

  // Questions state
  const [expandedTestId, setExpandedTestId] = useState<number | null>(null);
  const [questions, setQuestions] = useState<Record<number, Question[]>>({});
  const [questionsLoading, setQuestionsLoading] = useState<Record<number, boolean>>({});
  const [questionModalOpen, setQuestionModalOpen] = useState(false);
  const [questionTestId, setQuestionTestId] = useState<number | null>(null);
  const [qText, setQText] = useState('');
  const [qOptions, setQOptions] = useState<{ label: string; is_correct: boolean }[]>([
    { label: '', is_correct: true },
    { label: '', is_correct: false },
    { label: '', is_correct: false },
    { label: '', is_correct: false },
  ]);
  const [qExplanation, setQExplanation] = useState('');
  const [qSaving, setQSaving] = useState(false);

  // Delete state
  const [deleteTestId, setDeleteTestId] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchTests = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch('/api/tests');
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Testlarni yuklashda xatolik');
      }
      const data = await res.json();
      setTests(Array.isArray(data) ? data : data.exams || []);
    } catch (err: any) {
      setError(err.message || 'Testlarni yuklashda xatolik');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTests();
  }, [fetchTests]);

  const fetchQuestions = async (testId: number) => {
    try {
      setQuestionsLoading((prev) => ({ ...prev, [testId]: true }));
      const res = await fetch(`/api/tests/${testId}/questions`);
      if (!res.ok) throw new Error('Savollarni yuklashda xatolik');
      const data = await res.json();
      setQuestions((prev) => ({ ...prev, [testId]: Array.isArray(data) ? data : data.questions || [] }));
    } catch (err: any) {
      toast.error(err.message || 'Savollarni yuklashda xatolik');
    } finally {
      setQuestionsLoading((prev) => ({ ...prev, [testId]: false }));
    }
  };

  const toggleExpand = (testId: number) => {
    if (expandedTestId === testId) {
      setExpandedTestId(null);
    } else {
      setExpandedTestId(testId);
      if (!questions[testId]) {
        fetchQuestions(testId);
      }
    }
  };

  const openCreateModal = () => {
    setEditingTest(null);
    setFormTitle('');
    setFormDescription('');
    setFormLevel('A1');
    setFormDuration(30);
    setFormPassingScore('60');
    setIsModalOpen(true);
  };

  const openEditModal = (test: Test) => {
    setEditingTest(test);
    setFormTitle(test.title);
    setFormDescription(test.description || '');
    setFormLevel(test.cefr_level);
    setFormDuration(test.total_duration || 30);
    setFormPassingScore(test.passing_score?.toString() || '60');
    setIsModalOpen(true);
  };

  const handleSaveTest = async () => {
    if (!formTitle.trim()) {
      toast.error('Test sarlavhasini kiriting');
      return;
    }

    setFormSaving(true);
    try {
      const payload = {
        title: formTitle.trim(),
        description: formDescription.trim() || null,
        cefr_level: formLevel,
        total_duration: Number(formDuration) || 30,
        passing_score: Number(formPassingScore) || 60,
      };

      const url = editingTest ? `/api/tests/${editingTest.id}` : '/api/tests';
      const method = editingTest ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Saqlashda xatolik');
      }

      toast.success(editingTest ? '✅ Test yangilandi!' : '✅ Test yaratildi!');
      setIsModalOpen(false);
      await fetchTests();
    } catch (err: any) {
      toast.error(err.message || 'Saqlashda xatolik');
    } finally {
      setFormSaving(false);
    }
  };

  const handleDeleteTest = async () => {
    if (!deleteTestId) return;
    setDeleting(true);
    try {
      const res = await fetch(`/api/tests/${deleteTestId}`, { method: 'DELETE' });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "O&apos;chirishda xatolik");
      }
      toast.success('🗑️ Test o&apos;chirildi');
      setDeleteTestId(null);
      await fetchTests();
    } catch (err: any) {
      toast.error(err.message || "O&apos;chirishda xatolik");
    } finally {
      setDeleting(false);
    }
  };

  const openQuestionModal = (testId: number) => {
    setQuestionTestId(testId);
    setQText('');
    setQOptions([
      { label: '', is_correct: true },
      { label: '', is_correct: false },
      { label: '', is_correct: false },
      { label: '', is_correct: false },
    ]);
    setQExplanation('');
    setQuestionModalOpen(true);
  };

  const handleOptionChange = (index: number, value: string) => {
    setQOptions((prev) => prev.map((opt, i) => (i === index ? { ...opt, label: value } : opt)));
  };

  const handleCorrectChange = (index: number) => {
    setQOptions((prev) => prev.map((opt, i) => ({ ...opt, is_correct: i === index })));
  };

  const handleSaveQuestion = async () => {
    if (!questionTestId) return;
    if (!qText.trim()) {
      toast.error('Savol matnini kiriting');
      return;
    }
    const validOptions = qOptions.filter((opt) => opt.label.trim());
    if (validOptions.length < 2) {
      toast.error('Kamida 2 ta variant kiriting');
      return;
    }
    if (!validOptions.some((opt) => opt.is_correct)) {
      toast.error('To&apos;g&apos;ri javobni belgilang');
      return;
    }

    setQSaving(true);
    try {
      const correctOption = validOptions.find((opt) => opt.is_correct);
      const payload = {
        question_text: qText.trim(),
        question_type: 'multiple_choice',
        options: validOptions,
        correct_answer: correctOption?.label || '',
        explanation: qExplanation.trim() || null,
        points: 1,
        difficulty: 'medium',
      };

      const res = await fetch(`/api/tests/${questionTestId}/questions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Savol qo&apos;shishda xatolik');
      }

      toast.success('✅ Savol qo&apos;shildi!');
      setQuestionModalOpen(false);
      await fetchQuestions(questionTestId);
    } catch (err: any) {
      toast.error(err.message || 'Savol qo&apos;shishda xatolik');
    } finally {
      setQSaving(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      draft: 'bg-gray-100 text-gray-600',
      published: 'bg-green-100 text-green-700',
      active: 'bg-green-100 text-green-700',
      archived: 'bg-yellow-100 text-yellow-700',
    };
    const labels: Record<string, string> = {
      draft: 'Qoralama',
      published: 'Nashr etilgan',
      active: 'Faol',
      archived: 'Arxivlangan',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100 text-gray-600'}`}>
        {labels[status] || status}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Testlar</h1>
          <p className="text-gray-600 mt-1">CEFR testlarini yaratish va boshqarish</p>
        </div>
        <button
          onClick={openCreateModal}
          className="flex items-center gap-2 px-4 py-2.5 bg-primary text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus size={18} />
          Yangi test
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <AlertCircle size={18} className="mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium">Yuklashda xatolik</p>
            <p className="text-xs mt-1">{error}</p>
          </div>
          <button onClick={fetchTests} className="text-xs text-red-600 hover:underline">
            Qayta urinish
          </button>
        </div>
      )}

      {/* Tests List */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-lg border border-gray-200 p-5 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-3"></div>
              <div className="h-3 bg-gray-100 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      ) : tests.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <FileQuestion className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-semibold text-gray-900 mb-1">Testlar mavjud emas</h3>
          <p className="text-gray-500 mb-6">Birinchi testni yaratish orqali boshlang</p>
          <button
            onClick={openCreateModal}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-primary text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus size={18} />
            Yangi test yaratish
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {tests.map((test) => (
            <div key={test.id} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              {/* Test row */}
              <div className="p-5 flex items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-gray-900 truncate">{test.title}</h3>
                    <span className="px-2 py-0.5 bg-primary-100 text-primary-900 text-xs font-semibold rounded">
                      {test.cefr_level}
                    </span>
                    {getStatusBadge(test.status)}
                  </div>
                  {test.description && (
                    <p className="text-sm text-gray-500 mt-1 line-clamp-2">{test.description}</p>
                  )}
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                    <span>⏱ {test.total_duration || 0} daqiqa</span>
                    <span>🎯 O&apos;tish: {test.passing_score || 0}%</span>
                    <span>📝 {questions[test.id]?.length || 0} savol</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={() => openQuestionModal(test.id)}
                    className="p-2 text-gray-500 hover:text-primary hover:bg-dark-100 rounded-lg transition-colors"
                    title="Savol qo&apos;shish"
                  >
                    <Plus size={18} />
                  </button>
                  <button
                    onClick={() => openEditModal(test)}
                    className="p-2 text-gray-500 hover:text-primary hover:bg-dark-100 rounded-lg transition-colors"
                    title="Tahrirlash"
                  >
                    <Pencil size={18} />
                  </button>
                  <button
                    onClick={() => setDeleteTestId(test.id)}
                    className="p-2 text-gray-500 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    title="O&apos;chirish"
                  >
                    <Trash2 size={18} />
                  </button>
                  <button
                    onClick={() => toggleExpand(test.id)}
                    className="p-2 text-gray-500 hover:text-primary hover:bg-dark-100 rounded-lg transition-colors"
                    title={expandedTestId === test.id ? 'Yopish' : 'Savollarni ko&apos;rish'}
                  >
                    {expandedTestId === test.id ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                  </button>
                </div>
              </div>

              {/* Questions section */}
              {expandedTestId === test.id && (
                <div className="border-t border-gray-100 bg-gray-50/50 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-semibold text-gray-700">Savollar ({questions[test.id]?.length || 0})</h4>
                    <button
                      onClick={() => openQuestionModal(test.id)}
                      className="flex items-center gap-1 text-sm text-primary hover:text-primary-700 font-medium"
                    >
                      <Plus size={16} />
                      Savol qo&apos;shish
                    </button>
                  </div>

                  {questionsLoading[test.id] ? (
                    <div className="text-center py-4 text-sm text-gray-400">Yuklanmoqda...</div>
                  ) : !questions[test.id] || questions[test.id].length === 0 ? (
                    <div className="text-center py-4 text-sm text-gray-400">
                      Bu test uchun savollar mavjud emas
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {questions[test.id].map((q, idx) => (
                        <div key={q.id} className="bg-white rounded-lg border border-gray-200 p-4">
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex-1">
                              <p className="text-sm font-medium text-gray-800">
                                {idx + 1}. {q.question_text}
                              </p>
                              <div className="flex flex-wrap gap-2 mt-2">
                                {q.options?.map((opt, i) => (
                                  <span
                                    key={i}
                                    className={`px-2 py-1 rounded text-xs ${
                                      opt.is_correct
                                        ? 'bg-green-100 text-green-700'
                                        : 'bg-gray-100 text-gray-600'
                                    }`}
                                  >
                                    {opt.is_correct && <CheckCircle2 size={12} className="inline mr-1" />}
                                    {opt.label}
                                  </span>
                                ))}
                              </div>
                              {q.explanation && (
                                <p className="text-xs text-gray-500 mt-2">💡 {q.explanation}</p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Test Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full">
            <div className="flex items-center justify-between p-5 border-b">
              <h2 className="text-lg font-semibold text-gray-900">
                {editingTest ? 'Testni tahrirlash' : 'Yangi test yaratish'}
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={20} />
              </button>
            </div>
            <div className="p-5 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Sarlavha *</label>
                <input
                  type="text"
                  value={formTitle}
                  onChange={(e) => setFormTitle(e.target.value)}
                  placeholder="Masalan: CEFR A1 Daraja Testi"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tavsif</label>
                <textarea
                  value={formDescription}
                  onChange={(e) => setFormDescription(e.target.value)}
                  placeholder="Test haqida qisqa ma'lumot..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">CEFR daraja</label>
                  <select
                    value={formLevel}
                    onChange={(e) => setFormLevel(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    {CEFR_LEVELS.map((level) => (
                      <option key={level} value={level}>{level}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Davomiylik (daqiqa)</label>
                  <input
                    type="number"
                    value={formDuration}
                    onChange={(e) => setFormDuration(Number(e.target.value))}
                    min={1}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">O&apos;tish foizi (%)</label>
                <input
                  type="number"
                  value={formPassingScore}
                  onChange={(e) => setFormPassingScore(e.target.value)}
                  min={0}
                  max={100}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 p-5 border-t bg-gray-50 rounded-b-xl">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Bekor qilish
              </button>
              <button
                onClick={handleSaveTest}
                disabled={formSaving}
                className="px-4 py-2 text-sm font-medium bg-primary text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
              >
                {formSaving ? 'Saqlanmoqda...' : 'Saqlash'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Question Modal */}
      {questionModalOpen && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-5 border-b sticky top-0 bg-white">
              <h2 className="text-lg font-semibold text-gray-900">Yangi savol qo&apos;shish</h2>
              <button
                onClick={() => setQuestionModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={20} />
              </button>
            </div>
            <div className="p-5 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Savol matni *</label>
                <textarea
                  value={qText}
                  onChange={(e) => setQText(e.target.value)}
                  placeholder="Savolni kiriting..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Variantlar *</label>
                <div className="space-y-2">
                  {qOptions.map((opt, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <input
                        type="radio"
                        name="correct-option"
                        checked={opt.is_correct}
                        onChange={() => handleCorrectChange(idx)}
                        className="w-4 h-4 text-primary focus:ring-primary"
                        title="To&apos;g&apos;ri javob"
                      />
                      <input
                        type="text"
                        value={opt.label}
                        onChange={(e) => handleOptionChange(idx, e.target.value)}
                        placeholder={`Variant ${idx + 1}`}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                      {opt.is_correct && (
                        <span className="text-xs text-green-600 font-medium flex-shrink-0">✓ To&apos;g&apos;ri</span>
                      )}
                    </div>
                  ))}
                </div>
                <p className="text-xs text-gray-400 mt-2">Radio tugma orqali to&apos;g&apos;ri javobni belgilang</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Izoh (ixtiyoriy)</label>
                <textarea
                  value={qExplanation}
                  onChange={(e) => setQExplanation(e.target.value)}
                  placeholder="Javob haqida qo&apos;shimcha izoh..."
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 p-5 border-t bg-gray-50 rounded-b-xl">
              <button
                onClick={() => setQuestionModalOpen(false)}
                className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Bekor qilish
              </button>
              <button
                onClick={handleSaveQuestion}
                disabled={qSaving}
                className="px-4 py-2 text-sm font-medium bg-primary text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
              >
                {qSaving ? 'Saqlanmoqda...' : 'Savolni saqlash'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirm Modal */}
      {deleteTestId && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
            <div className="p-5">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Testni o&apos;chirish</h2>
              <p className="text-sm text-gray-600">
                Bu testni o&apos;chirishni tasdiqlaysizmi? Barcha savollar ham o&apos;chiriladi. Bu amal qaytarib bo&apos;lmaydi.
              </p>
            </div>
            <div className="flex justify-end gap-3 p-5 border-t bg-gray-50 rounded-b-xl">
              <button
                onClick={() => setDeleteTestId(null)}
                className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Bekor qilish
              </button>
              <button
                onClick={handleDeleteTest}
                disabled={deleting}
                className="px-4 py-2 text-sm font-medium bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 transition-colors"
              >
                {deleting ? "O&apos;chirilmoqda..." : "O&apos;chirish"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
