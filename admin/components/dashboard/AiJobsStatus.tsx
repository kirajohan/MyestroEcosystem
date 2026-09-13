// components/dashboard/AIJobsStatus.tsx
import { Bot, CheckCircle2, Clock, AlertCircle, Loader2 } from 'lucide-react';

interface AIJobs {
  pending: number;
  processing: number;
  completed: number;
  error: number;
}

interface AIJobsStatusProps {
  jobs?: AIJobs;
}

export function AIJobsStatus({ jobs }: AIJobsStatusProps) {
  if (!jobs) return null;

  const total = jobs.pending + jobs.processing + jobs.completed + jobs.error;

  const items = [
    {
      label: 'Kutilmoqda',
      value: jobs.pending,
      icon: Clock,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      label: 'Jarayonda',
      value: jobs.processing,
      icon: Loader2,
      color: 'text-orange-600',
      bg: 'bg-orange-50',
    },
    {
      label: 'Yakunlangan',
      value: jobs.completed,
      icon: CheckCircle2,
      color: 'text-emerald-600',
      bg: 'bg-emerald-50',
    },
    {
      label: 'Xatolik',
      value: jobs.error,
      icon: AlertCircle,
      color: 'text-red-600',
      bg: 'bg-red-50',
    },
  ];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-slate-900">AI holati</h3>
        <Bot className="w-5 h-5 text-orange-600" />
      </div>

      <div className="space-y-3">
        {items.map((item) => {
          const Icon = item.icon;
          const percentage = total > 0 ? (item.value / total) * 100 : 0;

          return (
            <div key={item.label} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`w-8 h-8 ${item.bg} rounded-lg flex items-center justify-center`}>
                    <Icon className={`w-4 h-4 ${item.color}`} />
                  </div>
                  <span className="text-sm font-medium text-slate-700">{item.label}</span>
                </div>
                <span className="text-sm font-bold text-slate-900">{item.value}</span>
              </div>
              
              {total > 0 && (
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${item.bg} transition-all duration-500`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {total > 0 && (
        <div className="mt-6 pt-6 border-t border-slate-100">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600">Jami vazifalar</span>
            <span className="font-bold text-slate-900">{total}</span>
          </div>
        </div>
      )}
    </div>
  );
}