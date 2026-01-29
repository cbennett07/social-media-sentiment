import { useState, useEffect, useCallback } from 'react';
import { api } from './api/client';
import type { Search, Theme, Entity, SentimentPoint, ItemsResponse } from './api/client';
import { SentimentGauge } from './components/SentimentGauge';
import { SentimentChart } from './components/SentimentChart';
import { ThemesList } from './components/ThemesList';
import { EntitiesList } from './components/EntitiesList';
import { ItemsTable } from './components/ItemsTable';
import { StatsCards } from './components/StatsCards';
import { CollectForm } from './components/CollectForm';
import { SearchSelector } from './components/SearchSelector';
import { SearchBar } from './components/SearchBar';
import { RefreshCw } from 'lucide-react';

function App() {
  const [searches, setSearches] = useState<Search[]>([]);
  const [selectedPhrase, setSelectedPhrase] = useState<string | null>(null);
  const [themes, setThemes] = useState<Theme[]>([]);
  const [entities, setEntities] = useState<Entity[]>([]);
  const [timeline, setTimeline] = useState<SentimentPoint[]>([]);
  const [items, setItems] = useState<ItemsResponse | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [granularity, setGranularity] = useState<'hour' | 'day' | 'week' | 'month'>('day');

  // Full-text search state
  const [searchQuery, setSearchQuery] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<ItemsResponse | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [searchesData, themesData, entitiesData, timelineData, itemsData] = await Promise.all([
        api.getSearches(),
        api.getThemes(selectedPhrase || undefined),
        api.getEntities(selectedPhrase || undefined),
        api.getSentimentTimeline(granularity, selectedPhrase || undefined),
        api.getItems({ search_phrase: selectedPhrase || undefined, page, page_size: 10 }),
      ]);

      setSearches(searchesData);
      setThemes(themesData);
      setEntities(entitiesData);
      setTimeline(timelineData);
      setItems(itemsData);
    } catch (err) {
      console.error('Failed to fetch data:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedPhrase, page, granularity]);

  useEffect(() => {
    if (!searchQuery) {
      fetchData();
    }
  }, [fetchData, searchQuery]);

  const handleSearch = async (query: string) => {
    setIsSearching(true);
    setSearchQuery(query);
    try {
      const results = await api.fullTextSearch({
        q: query,
        search_phrase: selectedPhrase || undefined,
        page: 1,
        page_size: 20
      });
      setSearchResults(results);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearchPageChange = async (newPage: number) => {
    if (!searchQuery) return;
    setIsSearching(true);
    try {
      const results = await api.fullTextSearch({
        q: searchQuery,
        search_phrase: selectedPhrase || undefined,
        page: newPage,
        page_size: 20
      });
      setSearchResults(results);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery(null);
    setSearchResults(null);
  };

  const selectedSearch = selectedPhrase
    ? searches.find((s) => s.phrase === selectedPhrase) || null
    : searches.length > 0
    ? {
        phrase: 'All',
        total_items: searches.reduce((sum, s) => sum + s.total_items, 0),
        first_collected: searches.reduce((min, s) => s.first_collected < min ? s.first_collected : min, searches[0]?.first_collected || ''),
        last_collected: searches.reduce((max, s) => s.last_collected > max ? s.last_collected : max, searches[0]?.last_collected || ''),
        first_published: searches.reduce((min, s) => s.first_published < min ? s.first_published : min, searches[0]?.first_published || ''),
        last_published: searches.reduce((max, s) => s.last_published > max ? s.last_published : max, searches[0]?.last_published || ''),
        avg_sentiment_score:
          searches.reduce((sum, s) => sum + s.avg_sentiment_score * s.total_items, 0) /
          searches.reduce((sum, s) => sum + s.total_items, 0) || 0,
        sentiment_distribution: searches.reduce(
          (acc, s) => ({
            positive: (acc.positive || 0) + (s.sentiment_distribution.positive || 0),
            negative: (acc.negative || 0) + (s.sentiment_distribution.negative || 0),
            neutral: (acc.neutral || 0) + (s.sentiment_distribution.neutral || 0),
          }),
          { positive: 0, negative: 0, neutral: 0 }
        ),
      }
    : null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Sentiment Analysis Dashboard</h1>
              <p className="text-sm text-gray-500">Monitor themes and sentiment across news sources</p>
            </div>
            <button
              onClick={fetchData}
              disabled={loading}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              title="Refresh data"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 space-y-6">
        {/* Collect Form */}
        <CollectForm onCollected={fetchData} />

        {/* Full-text Search */}
        <SearchBar
          onSearch={handleSearch}
          onClear={handleClearSearch}
          isSearching={isSearching}
          currentQuery={searchQuery}
        />

        {/* Search Results or Regular View */}
        {searchQuery && searchResults ? (
          <>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <p className="text-purple-800">
                Found <strong>{searchResults.total}</strong> articles matching "{searchQuery}"
                {selectedPhrase && ` in "${selectedPhrase}" collection`}
              </p>
            </div>
            <ItemsTable
              items={searchResults.items}
              total={searchResults.total}
              page={searchResults.page}
              pageSize={searchResults.page_size}
              onPageChange={handleSearchPageChange}
            />
          </>
        ) : (
          <>
            {/* Search Selector */}
            {searches.length > 0 && (
              <SearchSelector
                searches={searches}
                selected={selectedPhrase}
                onSelect={(phrase) => {
                  setSelectedPhrase(phrase);
                  setPage(1);
                }}
              />
            )}

            {/* Stats Cards */}
            <StatsCards search={selectedSearch} />

            {/* Sentiment Gauge */}
            {selectedSearch && (
              <SentimentGauge
                score={selectedSearch.avg_sentiment_score}
                label={`Overall Sentiment${selectedPhrase ? ` for "${selectedPhrase}"` : ''}`}
              />
            )}

            {/* Timeline Controls & Chart */}
            <div className="space-y-2">
              <div className="flex gap-2">
                {(['hour', 'day', 'week', 'month'] as const)
                  .filter((g) => {
                    // Calculate date range from published dates to determine valid granularities
                    if (searches.length === 0) return g === 'day';
                    const dates = searches.flatMap(s => [
                      new Date(s.first_published).getTime(),
                      new Date(s.last_published).getTime()
                    ]);
                    const minDate = Math.min(...dates);
                    const maxDate = Math.max(...dates);
                    const rangeMs = maxDate - minDate;
                    const rangeDays = rangeMs / (1000 * 60 * 60 * 24);

                    // Only show granularities that would yield at least 2 data points
                    if (g === 'hour') return rangeDays >= 0.1; // ~2.4 hours
                    if (g === 'day') return rangeDays >= 1;
                    if (g === 'week') return rangeDays >= 14;
                    if (g === 'month') return rangeDays >= 60; // ~2 months
                    return true;
                  })
                  .map((g) => (
                  <button
                    key={g}
                    onClick={() => setGranularity(g)}
                    className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                      granularity === g
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    {g.charAt(0).toUpperCase() + g.slice(1)}
                  </button>
                ))}
              </div>
              <SentimentChart data={timeline} granularity={granularity} />
            </div>

            {/* Themes and Entities */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ThemesList themes={themes} />
              <EntitiesList entities={entities} />
            </div>

            {/* Items Table */}
            {items && (
              <ItemsTable
                items={items.items}
                total={items.total}
                page={items.page}
                pageSize={items.page_size}
                onPageChange={setPage}
              />
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-8">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <p className="text-sm text-gray-500 text-center">
            Social Media Sentiment Analysis Platform
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
