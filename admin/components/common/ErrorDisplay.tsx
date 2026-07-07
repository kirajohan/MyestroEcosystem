import { AlertCircle, Redo } from 'lucide-react';

interface ErrorDisplayProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorDisplay({ message, onRetry }: ErrorDisplayProps) {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-sm">
        <div className="flex items-center gap-3 mb-3">
          <AlertCircle className="text-red-500" size={24} />
          <h3 className="font-semibold text-red-900">Error</h3>
        </div>
        <p className="text-red-700 mb-4">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
          >
            <Redo size={16} />
            Retry
          </button>
        )}
      </div>
    </div>
  );
}
