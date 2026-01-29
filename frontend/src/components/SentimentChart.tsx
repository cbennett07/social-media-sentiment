import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { format, parseISO } from 'date-fns';
import type { SentimentPoint } from '../api/client';

interface SentimentChartProps {
  data: SentimentPoint[];
  granularity: 'hour' | 'day' | 'week' | 'month';
}

export function SentimentChart({ data, granularity }: SentimentChartProps) {
  const formatDate = (dateStr: string) => {
    const date = parseISO(dateStr);
    switch (granularity) {
      case 'hour':
        return format(date, 'MMM d HH:mm');
      case 'day':
        return format(date, 'MMM d');
      case 'week':
        return format(date, 'MMM d');
      case 'month':
        return format(date, 'MMM yyyy');
    }
  };

  const chartData = data.map((point) => ({
    ...point,
    dateFormatted: formatDate(point.date),
  }));

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Sentiment Over Time</h3>
      {data.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-gray-400">
          No data available
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="dateFormatted" stroke="#6b7280" fontSize={12} />
            <YAxis domain={[-1, 1]} stroke="#6b7280" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
              }}
              formatter={(value) => [typeof value === 'number' ? value.toFixed(2) : value, 'Sentiment']}
            />
            <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" />
            <Line
              type="monotone"
              dataKey="avg_score"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ fill: '#3b82f6', strokeWidth: 2 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
