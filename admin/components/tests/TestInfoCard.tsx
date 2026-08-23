// admin/components/tests/TestInfoCard.tsx
'use client';

import { CheckCircle, XCircle, Clock, Target, FileQuestion } from 'lucide-react';
import { Test, CefrLevel } from '@/types/test';

interface TestInfoCardProps {
  test: Test;
  questionCount: number;
}

const CEFR_COLORS: Record<CefrLevel, string> = {
  A1: 'bg-green-100 text-green-800',
  A2: 'bg-emerald-100 text-emerald-800',
  B1: 'bg-blue-100 text-blue-800',
  B2: 'bg-indigo-100 text-indigo-800',
  C1: 'bg-purple-100 text-purple-800',
  C2: 'bg-rose-100 text-rose-800',
};

export default function TestInfoCard({ test, questionCount }: TestInfoCardProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-5">
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {/* CEFR Level */}
        <div className="flex flex-col">
          <span className="text-xs text-gray-500 font-medium uppercase tracking-wide">CEFR Daraja</span>
          <span className="mt-1">
            <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-sm font-semibold ${CEFR_COLORS[test.cefr_level] || 'bg-gray-100 text-gray-600'}`}>
              {test.cefr_level}
            </span>
          </span>
        </div>

        {/* Passing Score */}
        <div className="flex flex-col">
          <span className="text-xs text-gray-500 font-medium uppercase tracking-wide">O&apos;tish Balli</span>
          <span className="mt-1 flex items-center gap-1.5 text-sm font-medium text-gray-900">
            <Target size={14} className="text-blue-500" />
            {test.passing_score}%
          </span>
        </div>

        {/* Questions Count */}
        <div className="flex flex-col">
          <span className="text-xs text-gray-500 font-medium uppercase tracking-wide">Savollar</span>
          <span className="mt-1 flex items-center gap-1.5 text-sm font-medium text-gray-900">
            <FileQuestion size={14} className="text-indigo-500" />
            {questionCount} ta
          </span>
        </div>

        {/* Status */}
        <div className="flex flex-col">
          <span className="text-xs text-gray-500 font-medium uppercase tracking-wide">Holat</span>
          <span className="mt-1">
            {test.is_active ? (
              <span className="inline-flex items-center gap-1 text-sm font-medium text-green-600">
                <CheckCircle size={14} />
                Faol
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-sm font-medium text-gray-400">
                <XCircle size={14} />
                O&apos;chirilgan
              </span>
            )}
          </span>
        </div>

        {/* Created Date */}
        <div className="flex flex-col">
          <span className="text-xs text-gray-500 font-medium uppercase tracking-wide">Yaratilgan</span>
          <span className="mt-1 flex items-center gap-1.5 text-sm text-gray-600">
            <Clock size={14} className="text-gray-400" />
            {new Date(test.created_at).toLocaleDateString('uz-UZ', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
            })}
          </span>
        </div>
      </div>

      {/* Description */}
      {test.description && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <p className="text-sm text-gray-600">{test.description}</p>
        </div>
      )}
    </div>
  );
}
