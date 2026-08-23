// admin/app/tests/[id]/page.tsx
'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { toast } from 'sonner';
import {
  ArrowLeft,
  Plus,
  RefreshCw,
  AlertCircle,
  FileQuestion,
  Pencil,
  Trash2,
} from 'lucide-react';
import { Test, TestQuestion } from '@/types/test';
import { testsApi, ApiError } from '@/lib/api_client';
import TestInfoCard from '@/components/tests/TestInfoCard';
import QuestionList from '@/components/tests/QuestionList';
import QuestionFormModal from '@/components/tests/QuestionFormModal';
import DeleteConfirmModal from '@/components/tests/DeleteConfirmModal';
import TestFormModal from '@/components/tests/TestFormModal';

export default function TestDetailPage() {
  const params = useParams();
  const router = useRouter();
  const testId = Number(params.id);

  // ─── State ─────────────────────────────────────────────────
  const [test, setTest] = useState<Test | null>(null);
  const [questions, setQuestions] = useState<TestQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal states
  const [isTestFormOpen, setIsTestFormOpen] = useState(false);
  const [isQuestionFormOpen, setIsQuestionFormOpen] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState<TestQuestion | null>(null);
  const [deleteQuestionId, setDeleteQuestionId] = useState<number | null>(null);
  const [deleteTestId, setDeleteTestId] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);

  // ─── Fetch Data ────────────────────────────────────────────
  const fetchTestData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await testsApi.getQuestions(testId);
      setTest({
        id: data.id,
        title: data.title,
        description: data.description,
        cefr_level: data.cefr_level,
        passing_score: data.passing_score,
        is_active: data.is_active,
        created_at: data.created_at,
        updated_at: data.updated_at,
      });
      setQuestions(data.questions || []);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Testni yuklashda xatolik";
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }, [testId]);

  useEffect(() => {
    if (!isNaN(testId)) {
      fetchTestData();
    }
  }, [testId, fetchTestData]);

  // ─── Handlers ──────────────────────────────────────────────
  const handleOpenAddQuestion = () => {
    setEditingQuestion(null);
    setIsQuestionFormOpen(true);
  };

  const handleOpenEditQuestion = (question: TestQuestion) => {
    setEditingQuestion(question);
    setIsQuestionFormOpen(true);
  };

  const handleQuestionFormSuccess = () => {
    setIsQuestionFormOpen(false);
    setEditingQuestion(null);
    fetchTestData();
  };

  const handleDeleteQuestion = async () => {
    if (!deleteQuestionId) return;

    setDeleting(true);
    try {
      await testsApi.deleteQuestion(testId, deleteQuestionId);
      toast.success("✅ Savol o&apos;chirildi");
      setDeleteQuestionId(null);
      fetchTestData();
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Savolni o&apos;chirishda xatolik";
      toast.error(message);
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteTest = async () => {
    if (!deleteTestId) return;

    setDeleting(true);
    try {
      await testsApi.delete(deleteTestId);
      toast.success("✅ Test o&apos;chirildi");
      router.push('/tests');
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Testni o&apos;chirishda xatolik";
      toast.error(message);
    } finally {
      setDeleting(false);
    }
  };

  const handleTestFormSuccess = () => {
    setIsTestFormOpen(false);
    fetchTestData();
  };

  // ─── Render ────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="flex items-center gap-4">
          <div className="w-9 h-9 bg-gray-200 rounded-lg" />
          <div className="flex-1">
            <div className="h-5 bg-gray-200 rounded w-1/3" />
            <div className="h-3 bg-gray-100 rounded w-1/4 mt-2" />
          </div>
        </div>
        <div className="h-24 bg-gray-100 rounded-lg" />
        <div className="h-64 bg-gray-100 rounded-lg" />
      </div>
    );
  }

  if (error && !test) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <AlertCircle size={48} className="text-red-400 mb-4" />
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Xatolik yuz berdi</h2>
        <p className="text-gray-500 mb-4">{error}</p>
        <div className="flex gap-3">
          <button
            onClick={fetchTestData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Qayta urinish
          </button>
          <Link
            href="/tests"
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Testlarga qaytish
          </Link>
        </div>
      </div>
    );
  }

  if (!test) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/tests"
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="Testlarga qaytish"
          >
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-xl font-bold text-gray-900">{test.title}</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Savollar boshqaruvi • {questions.length} ta savol
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsTestFormOpen(true)}
            className="inline-flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Pencil size={14} />
            Testni tahrirlash
          </button>
          <button
            onClick={() => setDeleteTestId(test.id)}
            className="inline-flex items-center gap-2 px-3 py-2 text-sm border border-red-200 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
          >
            <Trash2 size={14} />
            O&apos;chirish
          </button>
        </div>
      </div>

      {/* Test Info Card */}
      <TestInfoCard test={test} questionCount={questions.length} />

      {/* Questions Section */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
        {/* Section Header */}
        <div className="flex items-center justify-between p-5 border-b border-gray-200">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Savollar</h2>
            <p className="text-sm text-gray-500 mt-0.5">
              Telegram Quiz Poll formatida ko&apos;rsatiladi
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchTestData}
              disabled={loading}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              title="Yangilash"
            >
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            </button>
            <button
              onClick={handleOpenAddQuestion}
              className="inline-flex items-center gap-2 px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus size={16} />
              Savol qo&apos;shish
            </button>
          </div>
        </div>

        {/* Questions List */}
        {questions.length === 0 ? (
          <div className="p-12 text-center">
            <FileQuestion className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <h3 className="text-sm font-medium text-gray-900 mb-1">Savollar mavjud emas</h3>
            <p className="text-sm text-gray-500 mb-4">
              Birinchi savolni qo&apos;shish orqali testni to&apos;ldiring
            </p>
            <button
              onClick={handleOpenAddQuestion}
              className="inline-flex items-center gap-2 px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus size={14} />
              Savol qo&apos;shish
            </button>
          </div>
        ) : (
          <QuestionList
            questions={questions}
            onEdit={handleOpenEditQuestion}
            onDelete={(id) => setDeleteQuestionId(id)}
          />
        )}
      </div>

      {/* Modals */}
      <TestFormModal
        isOpen={isTestFormOpen}
        onClose={() => setIsTestFormOpen(false)}
        onSuccess={handleTestFormSuccess}
        editingTest={test}
      />

      <QuestionFormModal
        isOpen={isQuestionFormOpen}
        onClose={() => {
          setIsQuestionFormOpen(false);
          setEditingQuestion(null);
        }}
        onSuccess={handleQuestionFormSuccess}
        testId={testId}
        editingQuestion={editingQuestion}
        nextOrderIndex={questions.length}
      />

      {/* Delete Question Confirm */}
      <DeleteConfirmModal
        isOpen={!!deleteQuestionId}
        onClose={() => setDeleteQuestionId(null)}
        onConfirm={handleDeleteQuestion}
        loading={deleting}
        title="Savolni o&apos;chirish"
        description="Bu savolni o&apos;chirishni tasdiqlaysizmi? Bu amal qaytarib bo&apos;lmaydi."
      />

      {/* Delete Test Confirm */}
      <DeleteConfirmModal
        isOpen={!!deleteTestId}
        onClose={() => setDeleteTestId(null)}
        onConfirm={handleDeleteTest}
        loading={deleting}
        title="Testni o&apos;chirish"
        description="Bu testni va barcha savollarini o&apos;chirishni tasdiqlaysizmi? Bu amal qaytarib bo&apos;lmaydi."
      />
    </div>
  );
}
