import { useState } from 'react';
import { Search, Loader2, Play } from 'lucide-react';
import { api } from '../api/client';

interface CollectFormProps {
  onCollected: () => void;
}

export function CollectForm({ onCollected }: CollectFormProps) {
  const [phrase, setPhrase] = useState('');
  const [isCollecting, setIsCollecting] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const handleCollect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!phrase.trim()) return;

    setIsCollecting(true);
    setStatus(null);

    try {
      const result = await api.collect({ phrase: phrase.trim() });
      setStatus({
        type: 'success',
        message: `Collected ${result.stats.total} items`,
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

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Collect & Process</h3>

      <form onSubmit={handleCollect} className="flex gap-2 mb-4">
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
      </form>

      {status && (
        <div
          className={`p-3 rounded-lg text-sm ${
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
