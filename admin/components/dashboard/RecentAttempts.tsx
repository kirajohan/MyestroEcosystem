// components/dashboard/RecentAttempts.tsx
import { Clock, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

interface Attempt {
  id: number;
  user_name: string;
  exam_title: string;
  status: string;
  score?: number;
  created_at: string;
}

interface RecentAttemptsProps {
  attempts: Attempt[];
}

export function RecentAttempts({ attempts }: RecentAttemptsProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-emerald-600" />;
      case 'scoring':
        return <Loader2 className="w-4 h-4 text-orange-600 animate-spin" />;
      case 'in_progress':
        return <Clock className="w-4 h-4 text-blue-600" />;
      default:
        return <AlertCircle className="w-4 h-4 text-slate-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-emerald-600 bg-emerald-50';
      case 'scoring':
        return 'text-orange-600 bg-orange-50';
      case 'in_progress':
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-slate-600 bg-slate-50';
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-slate-900">Oxirgi urinishlar</h3>
        <a href="/exam/attempts" className="text-sm text-orange-600 hover:text-orange-700 font-medium">
          Barchasi →
        </a>
      </div>

      {attempts.length === 0 ? (
        <div className="text-center py-12 text-slate-500">
          <Clock className="w-12 h-12 mx-auto mb-3 text-slate-300" />
          <p>Hali urinishlar yoq</p>
        </div>
      ) : (
        <div className="space-y-3">
          {attempts.slice(0, 5).map((attempt) => (
            <div
              key={attempt.id}
              className="flex items-center gap-4 p-4 bg-slate-50 rounded-xl hover:bg-slate-100 transition-colors"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <p className="font-semibold text-slate-900 truncate">
                    {attempt.user_name}
                  </p>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(attempt.status)}`}>
                    {attempt.status}
                  </span>
                </div>
                <p className="text-sm text-slate-600 truncate">{attempt.exam_title}</p>
              </div>

              <div className="text-right">
                {attempt.score !== null && attempt.score !== undefined && (
                  <p className="text-lg font-bold text-slate-900">
                    {attempt.score}
                  </p>
                )}
                <p className="text-xs text-slate-500">
                  {new Date(attempt.created_at).toLocaleString('uz-UZ', {
                    hour: '2-digit',
                    minute: '2-digit',
                    day: '2-digit',
                    month: 'short',
                  })}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}