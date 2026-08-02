'use client';

import { ContentItem } from '@/lib/types';
import { Video, FileText, Pencil, Trash2 } from 'lucide-react';

interface ContentTableProps {
  items: ContentItem[];
  isLoading: boolean;
  onEdit: (item: ContentItem) => void;
  onDelete: (item: ContentItem) => void;
}

export function ContentTable({ items, isLoading, onEdit, onDelete }: ContentTableProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow border border-gray-200 p-8 text-center text-gray-500">
        Yuklanmoqda...
      </div>
    );
  }

  if (!items || items.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow border border-gray-200 p-8 text-center text-gray-500">
        Hozircha hech qanday content mavjud emas.
      </div>
    );
  }

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('uz-UZ', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-3 text-xs font-semibold text-gray-600 uppercase tracking-wider">Turi</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-600 uppercase tracking-wider">Sarlavha</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-600 uppercase tracking-wider hidden md:table-cell">Izoh</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-600 uppercase tracking-wider hidden sm:table-cell">Sana</th>
              <th className="px-4 py-3 text-xs font-semibold text-gray-600 uppercase tracking-wider text-right">Amallar</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {items.map((item) => (
              <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    {item.content_type === 'video' ? (
                      <Video size={18} className="text-primary" />
                    ) : (
                      <FileText size={18} className="text-primary" />
                    )}
                    <span className="text-sm text-gray-600 capitalize hidden sm:inline">
                      {item.content_type}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="text-sm font-medium text-gray-900">{item.title}</div>
                </td>
                <td className="px-4 py-3 hidden md:table-cell">
                  <div className="text-sm text-gray-500 max-w-xs truncate">
                    {item.description || '—'}
                  </div>
                </td>
                <td className="px-4 py-3 hidden sm:table-cell">
                  <span className="text-sm text-gray-500">{formatDate(item.created_at)}</span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => onEdit(item)}
                      className="p-2 text-primary hover:bg-dark-100 rounded-lg transition-colors"
                      title="Tahrirlash"
                    >
                      <Pencil size={18} />
                    </button>
                    <button
                      onClick={() => onDelete(item)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="O'chirish"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
