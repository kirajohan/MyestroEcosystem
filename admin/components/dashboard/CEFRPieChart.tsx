'use client';

import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { CEFRDistribution } from '@/lib/types';

interface CEFRPieChartProps {
  data?: CEFRDistribution;
  isLoading?: boolean;
}

const CEFR_COLORS = {
  A1: '#3B82F6',
  A2: '#10B981',
  B1: '#F97316',
  B2: '#EF4444',
  C1: '#8B5CF6',
  C2: '#EC4899',
};

export function CEFRPieChart({ data, isLoading }: CEFRPieChartProps) {
  if (isLoading) {
    return (
      <div className="h-96 bg-gray-100 rounded-lg animate-pulse" />
    );
  }

  const chartData = data
    ? Object.entries(data)
        .filter(([, count]) => count > 0)
        .map(([level, count]) => ({
          name: level,
          value: count,
        }))
    : [];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        CEFR Taqsimoti
      </h3>
      {chartData.length === 0 ? (
        <div className="h-96 flex items-center justify-center text-gray-500">
          Ma&apos;lumot yo&apos;q
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value}`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry) => (
                <Cell
                  key={`cell-${entry.name}`}
                  fill={CEFR_COLORS[entry.name as keyof typeof CEFR_COLORS]}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#FFF7ED',
                border: '1px solid #F97316',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#000' }}
            />
            <Legend verticalAlign="bottom" height={36} />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
