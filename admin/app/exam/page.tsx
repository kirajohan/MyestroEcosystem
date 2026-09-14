'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  ClipboardCheck,
  Users,
  CheckCircle2,
  TrendingUp,
  FileText,
  Plus,
  BarChart3,
  Award,
} from 'lucide-react';

interface ExamStats {
  total_exams: number;
  total_attempts: number;
  completed_attempts: number;
  average_score: number;
}

export default function ExamDashboardPage() {
  const [stats, setStats] = useState<ExamStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        setStats({
          total_exams: 0,
          total_attempts: 0,
          completed_attempts: 0,
          average_score: 0,
        });
      } catch (error) {
        console.error('Stats yuklanmadi:', error);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[50vh]">
        <div className="w-8 h-8 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin" />
      </div>
    );
  }

  const statsCards = [
    {
      label: 'Jami examlar',
      value: stats?.total_exams || 0,
      icon: ClipboardCheck,
      color: 'orange',
      bg: 'bg-orange-50',
      iconColor: 'text-orange-600',
    },
    {
      label: 'Jami urinishlar',
      value: stats?.total_attempts || 0,
      icon: Users,
      color: 'blue',
      bg: 'bg-blue-50',
      iconColor: 'text-blue-600',
    },
    {
      label: 'Yakunlangan',
      value: stats?.completed_attempts || 0,
      icon: CheckCircle2,
      color: 'emerald',
      bg: 'bg-emerald-50',
      iconColor: 'text-emerald-600',
    },
    {
      label: 'Ortacha ball',
      value: `${stats?.average_score?.toFixed(1) || 0}%`,
      icon: TrendingUp,
      color: 'purple',
      bg: 'bg-purple-50',
      iconColor: 'text-purple-600',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Exam Dashboard</h1>
          <p className="text-sm md:text-base text-slate-600 mt-1">
            Imtihonlar statistikasi va boshqaruv
          </p>
        </div>
        <Link
          href="/exam/create"
          className="flex items-center justify-center gap-2 px-5 py-2.5 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl font-medium text-sm hover:from-orange-600 hover:to-orange-700 transition-all shadow-lg shadow-orange-500/20"
        >
          <Plus className="w-4 h-4" />
          Yangi Exam
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
        {statsCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <motion.div
              key={card.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white rounded-xl md:rounded-2xl border border-slate-200 p-4 md:p-5 shadow-sm"
            >
              <div className="flex items-center justify-between mb-2">
                <div className={`w-9 h-9 md:w-10 md:h-10 ${card.bg} rounded-lg flex items-center justify-center`}>
                  <Icon className={`w-4 h-4 md:w-5 md:h-5 ${card.iconColor}`} />
                </div>
              </div>
              <p className="text-xl md:text-2xl font-bold text-slate-900">{card.value}</p>
              <p className="text-xs text-slate-500 mt-1">{card.label}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Quick Links */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 bg-gradient-to-r from-orange-500 to-orange-600">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Award className="w-5 h-5" />
            Tezkor havolalar
          </h2>
        </div>

        <div className="p-5 grid grid-cols-1 md:grid-cols-3 gap-3">
          <Link
            href="/exam/exams"
            className="flex items-center gap-3 p-4 border border-slate-200 rounded-xl hover:bg-slate-50 hover:border-orange-200 transition-all group"
          >
            <div className="w-10 h-10 bg-orange-50 rounded-xl flex items-center justify-center group-hover:bg-orange-100 transition">
              <FileText className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="font-semibold text-slate-900 text-sm">Examlar</p>
              <p className="text-xs text-slate-500">Yaratish va boshqarish</p>
            </div>
          </Link>

          <Link
            href="/exam/attempts"
            className="flex items-center gap-3 p-4 border border-slate-200 rounded-xl hover:bg-slate-50 hover:border-blue-200 transition-all group"
          >
            <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center group-hover:bg-blue-100 transition">
              <BarChart3 className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="font-semibold text-slate-900 text-sm">Urinishlar</p>
              <p className="text-xs text-slate-500">Foydalanuvchi natijalari</p>
            </div>
          </Link>

          <Link
            href="/exam/create"
            className="flex items-center gap-3 p-4 border border-slate-200 rounded-xl hover:bg-slate-50 hover:border-emerald-200 transition-all group"
          >
            <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center group-hover:bg-emerald-100 transition">
              <Plus className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <p className="font-semibold text-slate-900 text-sm">Yangi Exam</p>
              <p className="text-xs text-slate-500">Imtihon yaratish</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}