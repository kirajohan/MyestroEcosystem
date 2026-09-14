'use client';

import Link from 'next/link';
import { Pencil, Trash2, ChevronRight, CheckCircle, XCircle, FileText } from 'lucide-react';
import { motion } from 'framer-motion';
import { Test, CefrLevel } from '@/types/test';

interface TestListTableProps {
  tests: Test[];
  onEdit: (test: Test) => void;
  onDelete: (id: number) => void;
}

const CEFR_COLORS: Record<CefrLevel, { bg: string; text: string; border: string }> = {
  A1: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  A2: { bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-200' },
  B1: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  B2: { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' },
  C1: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
  C2: { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },
};

export default function TestListTable({ tests, onEdit, onDelete }: TestListTableProps) {
  if (tests.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-12 text-center">
        <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <FileText className="w-8 h-8 text-slate-300" />
        </div>
        <h3 className="text-base font-semibold text-slate-900 mb-1">Testlar mavjud emas</h3>
        <p className="text-sm text-slate-500">Birinchi testni yaratish orqali boshlang</p>
      </div>
    );
  }

  return (
    <>
      {/* Desktop Table */}
      <div className="hidden md:block bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Table Header */}
        <div className="grid grid-cols-12 gap-4 px-6 py-3.5 bg-slate-50 border-b border-slate-200">
          <div className="col-span-4 text-xs font-semibold text-slate-600 uppercase tracking-wider">
            Sarlavha
          </div>
          <div className="col-span-1 text-xs font-semibold text-slate-600 uppercase tracking-wider">
            CEFR
          </div>
          <div className="col-span-2 text-xs font-semibold text-slate-600 uppercase tracking-wider">
            Otish balli
          </div>
          <div className="col-span-1 text-xs font-semibold text-slate-600 uppercase tracking-wider">
            Holat
          </div>
          <div className="col-span-2 text-xs font-semibold text-slate-600 uppercase tracking-wider">
            Yaratilgan
          </div>
          <div className="col-span-2 text-xs font-semibold text-slate-600 uppercase tracking-wider text-right">
            Amallar
          </div>
        </div>

        {/* Table Rows */}
        <div className="divide-y divide-slate-100">
          {tests.map((test, index) => {
            const cefrColor = CEFR_COLORS[test.cefr_level] || {
              bg: 'bg-slate-50',
              text: 'text-slate-600',
              border: 'border-slate-200',
            };

            return (
              <motion.div
                key={test.id}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03 }}
                className="grid grid-cols-12 gap-4 px-6 py-4 hover:bg-slate-50/50 transition-colors items-center group"
              >
                {/* Title + Description */}
                <div className="col-span-4 min-w-0">
                  <Link
                    href={`/tests/${test.id}`}
                    className="group/link flex items-center gap-2"
                  >
                    <span className="font-semibold text-slate-900 truncate group-hover/link:text-orange-600 transition-colors">
                      {test.title}
                    </span>
                    <ChevronRight
                      size={14}
                      className="text-slate-400 group-hover/link:text-orange-500 flex-shrink-0 transition-colors"
                    />
                  </Link>
                  {test.description && (
                    <p className="text-xs text-slate-500 truncate mt-0.5">{test.description}</p>
                  )}
                </div>

                {/* CEFR Level */}
                <div className="col-span-1">
                  <span
                    className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold border ${cefrColor.bg} ${cefrColor.text} ${cefrColor.border}`}
                  >
                    {test.cefr_level}
                  </span>
                </div>

                {/* Passing Score */}
                <div className="col-span-2">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-orange-400 to-orange-500 rounded-full"
                        style={{ width: `${test.passing_score}%` }}
                      />
                    </div>
                    <span className="text-sm font-semibold text-slate-700 w-10 text-right">
                      {test.passing_score}%
                    </span>
                  </div>
                </div>

                {/* Active Status */}
                <div className="col-span-1">
                  {test.is_active ? (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold">
                      <CheckCircle size={12} />
                      Faol
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-slate-100 text-slate-500 border border-slate-200 text-xs font-semibold">
                      <XCircle size={12} />
                      Ochirilgan
                    </span>
                  )}
                </div>

                {/* Created Date */}
                <div className="col-span-2 text-sm text-slate-500">
                  {new Date(test.created_at).toLocaleDateString('uz-UZ', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                  })}
                </div>

                {/* Actions */}
                <div className="col-span-2 flex items-center justify-end gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                  <Link
                    href={`/tests/${test.id}`}
                    className="p-2 text-slate-500 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                    title="Savollarni boshqarish"
                  >
                    <ChevronRight size={16} />
                  </Link>
                  <button
                    onClick={() => onEdit(test)}
                    className="p-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Tahrirlash"
                  >
                    <Pencil size={16} />
                  </button>
                  <button
                    onClick={() => onDelete(test.id)}
                    className="p-2 text-slate-500 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    title="Ochirish"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Mobile Cards */}
      <div className="md:hidden space-y-3">
        {tests.map((test, index) => {
          const cefrColor = CEFR_COLORS[test.cefr_level] || {
            bg: 'bg-slate-50',
            text: 'text-slate-600',
            border: 'border-slate-200',
          };

          return (
            <motion.div
              key={test.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white rounded-2xl border border-slate-200 shadow-sm p-4"
            >
              {/* Header */}
              <div className="flex items-start justify-between gap-3 mb-3">
                <Link href={`/tests/${test.id}`} className="flex-1 min-w-0">
                  <h3 className="font-semibold text-slate-900 truncate">{test.title}</h3>
                  {test.description && (
                    <p className="text-xs text-slate-500 truncate mt-0.5">{test.description}</p>
                  )}
                </Link>
                <span
                  className={`flex-shrink-0 inline-flex items-center px-2 py-1 rounded-lg text-xs font-bold border ${cefrColor.bg} ${cefrColor.text} ${cefrColor.border}`}
                >
                  {test.cefr_level}
                </span>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-2 mb-3">
                <div className="p-2 bg-slate-50 rounded-lg text-center">
                  <p className="text-xs text-slate-500">Otish</p>
                  <p className="text-sm font-bold text-slate-900">{test.passing_score}%</p>
                </div>
                <div className="p-2 bg-slate-50 rounded-lg text-center">
                  <p className="text-xs text-slate-500">Holat</p>
                  <p
                    className={`text-sm font-bold ${
                      test.is_active ? 'text-emerald-600' : 'text-slate-400'
                    }`}
                  >
                    {test.is_active ? 'Faol' : 'Ochir.'}
                  </p>
                </div>
                <div className="p-2 bg-slate-50 rounded-lg text-center">
                  <p className="text-xs text-slate-500">Sana</p>
                  <p className="text-xs font-semibold text-slate-700">
                    {new Date(test.created_at).toLocaleDateString('uz-UZ', {
                      month: 'short',
                      day: 'numeric',
                    })}
                  </p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 pt-3 border-t border-slate-100">
                <Link
                  href={`/tests/${test.id}`}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-orange-50 text-orange-700 rounded-lg font-medium text-xs hover:bg-orange-100 transition-colors"
                >
                  <ChevronRight size={14} />
                  <span>Savollar</span>
                </Link>
                <button
                  onClick={() => onEdit(test)}
                  className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="Tahrirlash"
                >
                  <Pencil size={16} />
                </button>
                <button
                  onClick={() => onDelete(test.id)}
                  className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  title="Ochirish"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </motion.div>
          );
        })}
      </div>
    </>
  );
}