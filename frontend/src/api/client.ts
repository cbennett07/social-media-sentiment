const API_BASE = '/api';

export interface Search {
  phrase: string;
  total_items: number;
  first_collected: string;
  last_collected: string;
  avg_sentiment_score: number;
  sentiment_distribution: {
    positive?: number;
    negative?: number;
    neutral?: number;
  };
}

export interface Item {
  id: string;
  source_type: string;
  source_name: string;
  url: string;
  title: string;
  published_at: string;
  sentiment: string;
  sentiment_score: number;
  summary: string;
}

export interface ItemsResponse {
  items: Item[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Theme {
  name: string;
  count: number;
  avg_confidence: number;
  sources: string[];
}

export interface Entity {
  name: string;
  count: number;
  avg_sentiment_score: number;
}

export interface SentimentPoint {
  date: string;
  avg_score: number;
  count: number;
  positive: number;
  negative: number;
  neutral: number;
}

export interface SourceBreakdown {
  source_type: string;
  source_name: string;
  count: number;
  avg_sentiment_score: number;
}

export interface CollectRequest {
  phrase: string;
  sources?: string[];
}

export interface CollectResponse {
  status: string;
  stats: {
    total: number;
    by_source: Record<string, number>;
    errors: string[];
  };
}

export interface ProcessResponse {
  status: string;
  stats: {
    processed: number;
    skipped: number;
    errors: string[];
  };
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }
  return response.json();
}

async function postJson<T>(url: string, body: unknown): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }
  return response.json();
}

export const api = {
  getSearches: () => fetchJson<Search[]>(`${API_BASE}/searches`),

  getItems: (params?: {
    search_phrase?: string;
    page?: number;
    page_size?: number;
    sentiment?: string;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.search_phrase) searchParams.set('search_phrase', params.search_phrase);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
    if (params?.sentiment) searchParams.set('sentiment', params.sentiment);
    return fetchJson<ItemsResponse>(`${API_BASE}/items?${searchParams}`);
  },

  getThemes: (searchPhrase?: string) => {
    const params = searchPhrase ? `?search_phrase=${encodeURIComponent(searchPhrase)}` : '';
    return fetchJson<Theme[]>(`${API_BASE}/themes${params}`);
  },

  getEntities: (searchPhrase?: string) => {
    const params = searchPhrase ? `?search_phrase=${encodeURIComponent(searchPhrase)}` : '';
    return fetchJson<Entity[]>(`${API_BASE}/entities${params}`);
  },

  getSentimentTimeline: (granularity: 'hour' | 'day' | 'week' | 'month' = 'day', searchPhrase?: string) => {
    const params = new URLSearchParams({ granularity });
    if (searchPhrase) params.set('search_phrase', searchPhrase);
    return fetchJson<SentimentPoint[]>(`${API_BASE}/sentiment/timeline?${params}`);
  },

  getSources: (searchPhrase?: string) => {
    const params = searchPhrase ? `?search_phrase=${encodeURIComponent(searchPhrase)}` : '';
    return fetchJson<SourceBreakdown[]>(`${API_BASE}/sources${params}`);
  },

  collect: (request: CollectRequest) =>
    postJson<CollectResponse>('/collect', request),

  process: () =>
    postJson<ProcessResponse>('/process', {}),
};
