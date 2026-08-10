import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  icon: LucideIcon;
  title: string;
  value: string | number;
  isLoading?: boolean;
}

export function StatsCard({
  icon: Icon,
  title,
  value,
  isLoading,
}: StatsCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-xl border border-dark-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium">{title}</p>
          {isLoading ? (
            <div className="h-8 w-16 mt-2 bg-gray-200 rounded animate-pulse" />
          ) : (
            <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          )}
        </div>
        <Icon className="text-primary-600" size={32} />
      </div>
    </div>
  );
}
