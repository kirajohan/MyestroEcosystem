export function SkeletonCard() {
  return (
    <div className="bg-white rounded-lg shadow p-6 border-l-4 border-primary animate-pulse">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="h-4 bg-gray-200 rounded w-32 mb-2" />
          <div className="h-8 bg-gray-200 rounded w-16" />
        </div>
        <div className="w-8 h-8 bg-gray-200 rounded" />
      </div>
    </div>
  );
}

export function SkeletonTable() {
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => (
              <th key={i} className="px-6 py-3">
                <div className="h-4 bg-gray-200 rounded w-16 animate-pulse" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {[1, 2, 3, 4, 5].map((row) => (
            <tr key={row} className="border-b">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((col) => (
                <td key={col} className="px-6 py-4">
                  <div className="h-4 bg-gray-200 rounded animate-pulse" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="bg-white rounded-lg shadow p-6 animate-pulse">
      <div className="h-6 bg-gray-200 rounded w-40 mb-4" />
      <div className="h-64 bg-gray-100 rounded" />
    </div>
  );
}

export function SkeletonLine() {
  return <div className="h-4 bg-gray-200 rounded w-full animate-pulse" />;
}
