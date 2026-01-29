import type { Entity } from '../api/client';

interface EntitiesListProps {
  entities: Entity[];
}

export function EntitiesList({ entities }: EntitiesListProps) {
  const getSentimentColor = (score: number) => {
    if (score < -0.3) return 'text-red-600 bg-red-50';
    if (score < 0.3) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Top Entities</h3>
      {entities.length === 0 ? (
        <div className="text-gray-400 text-center py-8">No entities found</div>
      ) : (
        <div className="space-y-2">
          {entities.slice(0, 15).map((entity) => (
            <div
              key={entity.name}
              className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
            >
              <div className="flex items-center gap-2">
                <span className="font-medium">{entity.name}</span>
                <span className="text-xs text-gray-400">({entity.count})</span>
              </div>
              <span
                className={`text-xs px-2 py-1 rounded-full ${getSentimentColor(
                  entity.avg_sentiment_score
                )}`}
              >
                {entity.avg_sentiment_score.toFixed(2)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
