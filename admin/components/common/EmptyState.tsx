import { Users, TrendingUp, AlertCircle } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: 'users' | 'chart' | 'error';
}

const icons = {
  users: Users,
  chart: TrendingUp,
  error: AlertCircle,
};

export function EmptyState({
  title,
  description,
  icon = 'users',
}: EmptyStateProps) {
  const Icon = icons[icon];

  return (
    <div className="bg-white rounded-lg shadow p-12 text-center">
      <Icon className="mx-auto text-gray-400 mb-4" size={48} />
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      {description && (
        <p className="text-gray-600">{description}</p>
      )}
    </div>
  );
}
