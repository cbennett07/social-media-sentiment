import type { Search } from '../api/client';

interface SearchSelectorProps {
  searches: Search[];
  selected: string | null;
  onSelect: (phrase: string | null) => void;
}

export function SearchSelector({ searches, selected, onSelect }: SearchSelectorProps) {
  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="text-sm text-gray-500">Filter by phrase:</span>
      <button
        onClick={() => onSelect(null)}
        className={`px-3 py-1 rounded-full text-sm transition-colors ${
          selected === null
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
      >
        All
      </button>
      {searches.map((search) => (
        <button
          key={search.phrase}
          onClick={() => onSelect(search.phrase)}
          className={`px-3 py-1 rounded-full text-sm transition-colors ${
            selected === search.phrase
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          {search.phrase} ({search.total_items})
        </button>
      ))}
    </div>
  );
}
