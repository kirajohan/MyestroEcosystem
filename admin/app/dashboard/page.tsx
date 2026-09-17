'use client';

import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { 
  Users, 
  ClipboardCheck, 
  Bot, 
  Video, 
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertCircle,
  Activity,
  Sparkles
} from 'lucide-react';
import api from '@/lib/api';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { ActivityChart } from '@/components/dashboard/ActivityChart';
import { CEFRPieChart } from '@/components/dashboard/CEFRPieChart';
import { RecentAttempts } from '@/components/dashboard/RecentAttempts';
import { AIJobsStatus } from '@/components/dashboard/AiJobsStatus';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { ErrorDisplay } from '@/components/common/ErrorDisplay';
import { SkeletonCard, SkeletonChart } from '@/components/common/Skeleton';
import { GlobalSwitches } from '@/components/dashboard/GlobalSwitches';

interface DashboardStats {
  total_users: number;
  total_exams: number;
  total_attempts: number;
  completed_attempts: number;
  pending_ai_jobs: number;
  total_content: number;
  active_users_7d: number;
  today_messages: number;
}

interface DashboardData {
  stats: DashboardStats;
  recent_attempts: any[];
  ai_jobs: {
    pending: number;
    processing: number;
    completed: number;
    error: number;
  };
}

export default function DashboardPage() {
  const { data, isLoading, error } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await api.get('/stats/dashboard');
      return response.data;
    },
    staleTime: 30000,
    refetchInterval: 60000,
  });

  if (error) {
    return (
      <ErrorDisplay
        message="Dashboard ma'lumotlarini yuklashda xatolik"
        onRetry={() => window.location.reload()}
      />
    );
  }

  return (
    <div className="space-y-6 md:space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-sm md:text-base text-slate-600 mt-1">Tizim statistikasi va oxirgi faolliklar</p>
        </div>
        <div className="flex items-center gap-2 text-xs md:text-sm text-slate-500">
          <Clock className="w-4 h-4" />
          <span>Oxirgi yangilanish: {new Date().toLocaleTimeString('uz-UZ')}</span>
        </div>
      </div>

      {/* Stats Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-6">
        {isLoading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            <StatsCard
              icon={Users}
              title="Jami foydalanuvchilar"
              value={data?.stats.total_users ?? 0}
              subtitle={`${data?.stats.active_users_7d ?? 0} faol (7 kun)`}
              trend={12}
              color="blue"
            />
            <StatsCard
              icon={ClipboardCheck}
              title="Imtihon urinishlari"
              value={data?.stats.total_attempts ?? 0}
              subtitle={`${data?.stats.completed_attempts ?? 0} yakunlangan`}
              trend={8}
              color="orange"
            />
            <StatsCard
              icon={Bot}
              title="AI vazifalar"
              value={(data?.ai_jobs.pending ?? 0) + (data?.ai_jobs.processing ?? 0)}
              subtitle={`${data?.ai_jobs.completed ?? 0} yakunlangan`}
              color="green"
            />
            <StatsCard
              icon={Video}
              title="Kontent"
              value={data?.stats.total_content ?? 0}
              subtitle="Video va fayllar"
              color="purple"
            />
          </>
        )}
      </div>
    {/* 
    // Stats Cards Grid dan KEYIN, Charts Grid dan OLDIN qo'shish:
        */}
      {/* Global Switches - NEW */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
        <div className="lg:col-span-2">
          <GlobalSwitches />
        </div>
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 mb-4">Tezkor Harakatlar</h3>
          <div className="space-y-2">
            <button
              onClick={() => window.location.href = '/users'}
              className="w-full flex items-center gap-3 p-3 bg-slate-50 hover:bg-slate-100 rounded-xl transition-colors text-left"
            >
              <Users className="w-5 h-5 text-slate-600" />
              <div>
                <p className="text-sm font-medium text-slate-900">Foydalanuvchilar</p>
                <p className="text-xs text-slate-500">Boshqarish</p>
              </div>
            </button>
            <button
              onClick={() => window.location.href = '/content'}
              className="w-full flex items-center gap-3 p-3 bg-slate-50 hover:bg-slate-100 rounded-xl transition-colors text-left"
            >
              <Video className="w-5 h-5 text-slate-600" />
              <div>
                <p className="text-sm font-medium text-slate-900">Kontent</p>
                <p className="text-xs text-slate-500">Darsliklar</p>
              </div>
            </button>
            <button
              onClick={() => window.location.href = '/broadcast'}
              className="w-full flex items-center gap-3 p-3 bg-slate-50 hover:bg-slate-100 rounded-xl transition-colors text-left"
            >
              <Activity className="w-5 h-5 text-slate-600" />
              <div>
                <p className="text-sm font-medium text-slate-900">Broadcast</p>
                <p className="text-xs text-slate-500">Ommaviy xabar</p>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        {isLoading ? (
          <>
            <SkeletonChart />
            <SkeletonChart />
          </>
        ) : (
          <>
            <ActivityChart />
            <CEFRPieChart />
          </>
        )}
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
        {/* Recent Attempts */}
        <div className="lg:col-span-2">
          {isLoading ? (
            <SkeletonChart />
          ) : (
            <RecentAttempts attempts={data?.recent_attempts ?? []} />
          )}
        </div>

        {/* AI Jobs Status */}
        <div>
          {isLoading ? (
            <SkeletonChart />
          ) : (
            <AIJobsStatus jobs={data?.ai_jobs} />
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <QuickActions />
    </div>
  );
}