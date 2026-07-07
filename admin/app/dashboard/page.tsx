'use client';

import { Users, MessageCircle, Activity, AlertCircle } from 'lucide-react';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { ActivityChart } from '@/components/dashboard/ActivityChart';
import { CEFRPieChart } from '@/components/dashboard/CEFRPieChart';
import { ErrorDisplay } from '@/components/common/ErrorDisplay';
import { SkeletonCard, SkeletonChart } from '@/components/common/Skeleton';
import { useStats, useActivity, useCEFR } from '@/hooks/useDashboard';

export default function DashboardPage() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useStats();
  const {
    data: activity,
    isLoading: activityLoading,
    error: activityError,
  } = useActivity();
  const { data: cefr, isLoading: cefrLoading, error: cefrError } = useCEFR();

  if (statsError || activityError || cefrError) {
    return (
      <ErrorDisplay
        message="Dashboard ma&apos;lumotlarini yuklashda xatolik"
        onRetry={() => window.location.reload()}
      />
    );
  }

  return (
    <div className="space-y-8">
      {/* Stats Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsLoading ? (
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
              title="Jami Foydalanuvchilar"
              value={stats?.total_users ?? 0}
              isLoading={false}
            />
            <StatsCard
              icon={MessageCircle}
              title="Bugun Xabarlar"
              value={stats?.today_messages ?? 0}
              isLoading={false}
            />
            <StatsCard
              icon={Activity}
              title="Faol (7 kun)"
              value={stats?.active_users_7d ?? 0}
              isLoading={false}
            />
            <StatsCard
              icon={AlertCircle}
              title="Xatolar"
              value={stats?.error_count ?? 0}
              isLoading={false}
            />
          </>
        )}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {activityLoading ? (
          <SkeletonChart />
        ) : (
          <ActivityChart data={activity} isLoading={false} />
        )}
        {cefrLoading ? (
          <SkeletonChart />
        ) : (
          <CEFRPieChart data={cefr} isLoading={false} />
        )}
      </div>
    </div>
  );
}
