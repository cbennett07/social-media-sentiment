interface SentimentGaugeProps {
  score: number;
  label?: string;
}

export function SentimentGauge({ score, label }: SentimentGaugeProps) {
  // Score ranges from -1 (negative) to 1 (positive)
  const percentage = ((score + 1) / 2) * 100;

  const getColor = (score: number) => {
    if (score < -0.3) return 'bg-red-500';
    if (score < 0.3) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getSentimentLabel = (score: number) => {
    if (score < -0.3) return 'Negative';
    if (score < 0.3) return 'Neutral';
    return 'Positive';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-sm font-medium text-gray-500 mb-2">{label || 'Sentiment'}</h3>
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full ${getColor(score)} transition-all duration-500`}
              style={{ width: `${percentage}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>Negative</span>
            <span>Neutral</span>
            <span>Positive</span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold">{score.toFixed(2)}</div>
          <div className={`text-sm ${score < -0.3 ? 'text-red-600' : score < 0.3 ? 'text-yellow-600' : 'text-green-600'}`}>
            {getSentimentLabel(score)}
          </div>
        </div>
      </div>
    </div>
  );
}
