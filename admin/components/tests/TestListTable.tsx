// admin/components/tests/TestListTable.tsx
'use client';

import Link from 'next/link';
import { Pencil, Trash2, ChevronRight, CheckCircle, XCircle } from 'lucide-react';
import { Test, CefrLevel } from '@/types/test';

interface TestListTableProps {
  tests: Test[];
  onEdit: (test: Test) => void;
  onDelete: (id: number) => void;
}

const CEFR_COLORS: Record<CefrLevel, string> = {
  A1: 'bg-green-100 text-green-800',
  A2: 'bg-emerald-100 text-emerald-800',
  B1: 'bg-blue-100 text-blue-800',
  B2: 'bg-indigo-100 text-indigo-800',
  C1: 'bg-purple-100 text-purple-800',
  C2: 'bg-rose-100 text-rose-800',
};

export default function TestListTable({ tests, onEdit, onDelete }: TestListTableProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
      {/* Table Header */}
      <div className="hidden md:grid grid-cols-12 gap-4 px-5 py-3 bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-500 uppercase tracking-wider">
        <div className="col-span-4">Sarlavha</div>
        <div className="col-span-1">CEFR</div>
        <div className="col-span-2">O&apos;tish balli</div>
        <div className="col-span-1">Holat</div>
        <div className="col-span-2">Yaratilgan</div>
        <div className="col-span-2 text-right">Amallar</div>
      </div>

      {/* Table Rows */}
      <div className="divide-y divide-gray-100">
        {tests.map((test) => (
          <div
            key={test.id}
            className="grid grid-cols-1 md:grid-cols-12 gap-2 md:gap-4 px-5 py-4 hover:bg-gray-50/50 transition-colors items-center"
          >
            {/* Title + Description */}
            <div className="col-span-4 min-w-0">
              <Link
                href={`/tests/${test.id}`}
                className="group flex items-center gap-2"
              >
                <span className="font-medium text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                  {test.title}
                </span>
                <ChevronRight size={14} className="text-gray-400 group-hover:text-blue-500 flex-shrink-0" />
              </Link>
              {test.description && (
                <p className="text-sm text-gray-500 truncate mt-0.5">{test.description}</p>
              )}
            </div>

            {/* CEFR Level */}
            <div className="col-span-1">
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${CEFR_COLORS[test.cefr_level] || 'bg-gray-100 text-gray-600'}`}
              >
                {test.cefr_level}
              </span>
            </div>

            {/* Passing Score */}
            <div className="col-span-2 text-sm text-gray-600">
              🎯 {test.passing_score}%
            </div>

            {/* Active Status */}
            <div className="col-span-1">
              {test.is_active ? (
                <span className="inline-flex items-center gap-1 text-xs text-green-600 font-medium">
                  <CheckCircle size={14} />
                  Faol
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-xs text-gray-400 font-medium">
                  <XCircle size={14} />
                  O&apos;chirilgan
                </span>
              )}
            </div>

            {/* Created Date */}
            <div className="col-span-2 text-sm text-gray-500">
              {new Date(test.created_at).toLocaleDateString("uz-UZ", {
                year: "numeric",
                month: "short",
                day: "numeric",
              })}
            </div>

            {/* Actions */}
            <div className="col-span-2 flex items-center justify-end gap-1">
              <Link
                href={`/tests/${test.id}`}
                className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Savollarni boshqarish"
              >
                <ChevronRight size={16} />
              </Link>
              <button
                onClick={() => onEdit(test)}
                className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Tahrirlash"
              >
                <Pencil size={16} />
              </button>
              <button
                onClick={() => onDelete(test.id)}
                className="p-2 text-gray-500 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                title="O&apos;chirish"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
