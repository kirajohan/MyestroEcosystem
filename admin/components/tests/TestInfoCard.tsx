'use client';

import { CheckCircle, XCircle, Clock, Target, FileQuestion, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';
import { Test, CefrLevel } from '@/types/test';

interface TestInfoCardProps {
  test: Test;
  questionCount: number;
}

const CEFR_COLORS: Record<CefrLevel, { bg: string; text: string; border: string }> = {
  A1: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  A2: { bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-200' },
  B1: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  B2: { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' },
  C1: { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
  C2: { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },
};

export default function TestInfoCard({ test, questionCount }: TestInfoCardProps) {
  const cefrColor = CEFR_COLORS[test.cefr_level] || {
    bg: 'bg-slate-50',
    text: 'text-slate-600',
    border: 'border-slate-200',
  };

  const stats = [
    {
      label: 'CEFR Daraja',
      value: test.cefr_level,
      type: 'cefr' as const,
    },
    {
      label: 'Otish Balli',
      value: `${test.passing_score}%`,
      icon: Target,
      iconColor: 'text-orange-500',
    },
    {
      label: 'Savollar',
      value: `${questionCount} ta`,
      icon: FileQuestion,
      iconColor: 'text-blue-500',
    },
    {
      label: 'Holat',
      value: test.is_active ? 'Faol' : 'Ochirilgan',
      type: 'status' as const,
    },
    {
      label: 'Yaratilgan',
      value: new Date(test.created_at).toLocaleDateString('uz-UZ', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      }),
      icon: Calendar,
      iconColor: 'text-slate-500',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
    >
      {/* Header gradient */}
      <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
            <FileQuestion className="w-5 h-5 text-white" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-bold text-white">{test.title}</h2>
            <p className="text-xs text-white/80">Test malumotlari</p>
          </div>
        </div>
      </div>

      {/* Stats grid */}
      <div className="p-5">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="p-3 bg-slate-50 rounded-xl"
            >
              <p className="text-xs text-slate-500 font-medium uppercase tracking-wide mb-1.5">
                {stat.label}
              </p>

              {stat.type === 'cefr' && (
                <span
                  className={`inline-flex items-center px-2.5 py-1 rounded-lg text-sm font-bold border ${cefrColor.bg} ${cefrColor.text} ${cefrColor.border}`}
                >
                  {stat.value}
                </span>
              )}

              {stat.type === 'status' && (
                <div>
                  {test.is_active ? (
                    <span className="inline-flex items-center gap-1 text-sm font-semibold text-emerald-600">
                      <CheckCircle size={14} />
                      {stat.value}
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-sm font-semibold text-slate-400">
                      <XCircle size={14} />
                      {stat.value}
                    </span>
                  )}
                </div>
              )}

              {!stat.type && stat.icon && (
                <div className="flex items-center gap-1.5">
                  <stat.icon size={14} className={stat.iconColor} />
                  <span className="text-sm font-semibold text-slate-900">{stat.value}</span>
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Description */}
        {test.description && (
          <div className="mt-4 pt-4 border-t border-slate-100">
            <p className="text-sm text-slate-600 leading-relaxed">{test.description}</p>
          </div>
        )}

        {/* Passing score progress bar */}
        <div className="mt-4 pt-4 border-t border-slate-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-600">Otish balli</span>
            <span className="text-sm font-bold text-slate-900">{test.passing_score}%</span>
          </div>
          <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${test.passing_score}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              className="h-full bg-gradient-to-r from-orange-400 to-orange-500 rounded-full"
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
}