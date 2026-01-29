import { FileText, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { Search } from '../api/client';

interface StatsCardsProps {
  search: Search | null;
}

export function StatsCards({ search }: StatsCardsProps) {
  if (!search) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-16"></div>
          </div>
        ))}
      </div>
    );
  }

  const distribution = search.sentiment_distribution;
  const total = (distribution.positive || 0) + (distribution.negative || 0) + (distribution.neutral || 0);

  const stats = [
    {
      label: 'Total Items',
      value: search.total_items,
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      label: 'Positive',
      value: distribution.positive || 0,
      percent: total > 0 ? ((distribution.positive || 0) / total * 100).toFixed(0) : 0,
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      label: 'Neutral',
      value: distribution.neutral || 0,
      percent: total > 0 ? ((distribution.neutral || 0) / total * 100).toFixed(0) : 0,
      icon: Minus,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
    },
    {
      label: 'Negative',
      value: distribution.negative || 0,
      percent: total > 0 ? ((distribution.negative || 0) / total * 100).toFixed(0) : 0,
      icon: TrendingDown,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div key={stat.label} className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">{stat.label}</p>
              <p className="text-2xl font-bold mt-1">{stat.value}</p>
              {stat.percent !== undefined && (
                <p className="text-xs text-gray-400">{stat.percent}% of total</p>
              )}
            </div>
            <div className={`p-3 rounded-full ${stat.bgColor}`}>
              <stat.icon className={`w-6 h-6 ${stat.color}`} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
