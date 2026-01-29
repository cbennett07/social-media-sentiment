import { useState } from 'react';
import { Search, Loader2, Play, Calendar } from 'lucide-react';
import { format, subDays } from 'date-fns';
import { api } from '../api/client';

interface CollectFormProps {
  onCollected: () => void;
}

export function CollectForm({ onCollected }: CollectFormProps) {
  const [phrase, setPhrase] = useState('');
  const [daysBack, setDaysBack] = useState(7);
  const [isCollecting, setIsCollecting] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const today = new Date();
  const startDate = subDays(today, daysBack);

  const handleCollect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phrase.trim()) return;

    setIsCollecting(true);
    setStatus(null);

    try {
      const result = await api.collect({
        phrase: phrase.trim(),
        start_date: startDate.toISOString(),
        end_date: today.toISOString(),
      });
      setStatus({
        type: 'success',
        message: `Collected ${result.stats.total} items from the last ${daysBack} days`,
      });
      onCollected();
    } catch (err) {
      setStatus({
        type: 'error',
        message: err instanceof Error ? err.message : 'Collection failed',
      });
    } finally {
      setIsCollecting(false);
    }
  };

  const handleProcess = async () => {
    setIsProcessing(true);
    setStatus(null);

    try {
      const result = await api.process();
      setStatus({
        type: 'success',
        message: `Processed ${result.stats.processed} items`,
      });
      onCollected();
    } catch (err) {
      setStatus({
        type: 'error',
        message: err instanceof Error ? err.message : 'Processing failed',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const getSliderBackground = () => {
    const percentage = (daysBack / 60) * 100;
    return `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${percentage}%, #e5e7eb ${percentage}%, #e5e7eb 100%)`;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Collect & Process</h3>

      <form onSubmit={handleCollect} className="space-y-4">
        {/* Search phrase input */}
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={phrase}
              onChange={(e) => setPhrase(e.target.value)}
              placeholder="Enter search phrase..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            type="submit"
            disabled={isCollecting || !phrase.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isCollecting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            Collect
          </button>
          <button
            type="button"
            onClick={handleProcess}
            disabled={isProcessing}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isProcessing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            Process
          </button>
        </div>

        {/* Date range slider */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Calendar className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Collection Date Range</span>
          </div>

          <div className="space-y-2">
            <input
              type="range"
              min="1"
              max="60"
              value={daysBack}
              onChange={(e) => setDaysBack(parseInt(e.target.value))}
              className="w-full h-2 rounded-lg appearance-none cursor-pointer"
              style={{ background: getSliderBackground() }}
            />

            <div className="flex justify-between items-center text-sm">
              <span className="text-gray-500">
                {format(startDate, 'MMM d, yyyy')}
              </span>
              <span className="font-medium text-blue-600">
                Last {daysBack} day{daysBack !== 1 ? 's' : ''}
              </span>
              <span className="text-gray-500">
                {format(today, 'MMM d, yyyy')}
              </span>
            </div>

            {/* Quick select buttons */}
            <div className="flex gap-2 mt-2">
              {[
                { label: '24h', days: 1 },
                { label: '7d', days: 7 },
                { label: '14d', days: 14 },
                { label: '30d', days: 30 },
                { label: '60d', days: 60 },
              ].map(({ label, days }) => (
                <button
                  key={days}
                  type="button"
                  onClick={() => setDaysBack(days)}
                  className={`px-3 py-1 text-xs rounded-full transition-colors ${
                    daysBack === days
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </form>

      {status && (
        <div
          className={`mt-4 p-3 rounded-lg text-sm ${
            status.type === 'success'
              ? 'bg-green-50 text-green-800'
              : 'bg-red-50 text-red-800'
          }`}
        >
          {status.message}
        </div>
      )}
    </div>
  );
}
