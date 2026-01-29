import type { Theme } from '../api/client';

interface ThemesListProps {
  themes: Theme[];
}

export function ThemesList({ themes }: ThemesListProps) {
  const maxCount = Math.max(...themes.map((t) => t.count), 1);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Top Themes</h3>
      {themes.length === 0 ? (
        <div className="text-gray-400 text-center py-8">No themes found</div>
      ) : (
        <div className="space-y-3">
          {themes.slice(0, 10).map((theme) => (
            <div key={theme.name}>
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium truncate" title={theme.name}>
                  {theme.name}
                </span>
                <span className="text-gray-500 ml-2 shrink-0">
                  {theme.count} ({(theme.avg_confidence * 100).toFixed(0)}%)
                </span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500 rounded-full"
                  style={{ width: `${(theme.count / maxCount) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
