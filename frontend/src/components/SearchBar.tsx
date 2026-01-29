import { useState } from 'react';
import { Search, X } from 'lucide-react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  onClear: () => void;
  isSearching: boolean;
  currentQuery: string | null;
}

export function SearchBar({ onSearch, onClear, isSearching, currentQuery }: SearchBarProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleClear = () => {
    setQuery('');
    onClear();
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search articles (e.g., 'climate change', 'election')..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
        <button
          type="submit"
          disabled={isSearching || !query.trim()}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Search className="w-4 h-4" />
          Search
        </button>
        {currentQuery && (
          <button
            type="button"
            onClick={handleClear}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 flex items-center gap-2"
          >
            <X className="w-4 h-4" />
            Clear
          </button>
        )}
      </form>
      {currentQuery && (
        <div className="mt-2 text-sm text-purple-600">
          Showing results for: <strong>"{currentQuery}"</strong>
        </div>
      )}
    </div>
  );
}
