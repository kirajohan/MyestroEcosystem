'use client';

import { Eye, Pencil, Trash2 } from 'lucide-react';
import { UserResponse } from '@/lib/types';
import { Badge } from '@/components/ui/Badge';
import { formatDate } from '@/lib/utils';

interface UserTableProps {
  users: UserResponse[];
  isLoading?: boolean;
  onView?: (user: UserResponse) => void;
  onEdit?: (user: UserResponse) => void;
  onDelete?: (user: UserResponse) => void;
}

export function UserTable({
  users,
  isLoading,
  onView,
  onEdit,
  onDelete,
}: UserTableProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">Role</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">CEFR</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">AI</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">Last Login</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody>
            {[1, 2, 3, 4, 5].map((i) => (
              <tr key={i}>
                <td colSpan={9} className="px-6 py-4">
                  <div className="h-4 bg-gray-200 rounded animate-pulse" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (users.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-12 text-center">
        <p className="text-gray-500">Foydalanuvchilar topilmadi</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">ID</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">Name</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">Email</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">Role</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">CEFR</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">AI</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">Last Login</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr
              key={user.id}
              className="border-b hover:bg-orange-50 transition-colors"
            >
              <td className="px-6 py-4 text-sm text-gray-900">{user.id}</td>
              <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                {user.full_name}
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">{user.email}</td>
              <td className="px-6 py-4 text-sm">
                <Badge variant={user.role === 'admin' ? 'admin' : 'user'}>
                  {user.role}
                </Badge>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">{user.cefr_level}</td>
              <td className="px-6 py-4 text-sm">
                <Badge
                  variant={user.is_active ? 'active' : 'blocked'}
                >
                  {user.is_active ? 'Active' : 'Blocked'}
                </Badge>
              </td>
              <td className="px-6 py-4 text-sm">
                <Badge variant={user.ai_enabled ? 'on' : 'off'}>
                  {user.ai_enabled ? 'ON' : 'OFF'}
                </Badge>
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                {formatDate(user.last_login_at)}
              </td>
              <td className="px-6 py-4 text-sm">
                <div className="flex items-center gap-2">
                  {onView && (
                    <button
                      onClick={() => onView(user)}
                      className="p-2 hover:bg-gray-100 rounded transition-colors"
                      title="View"
                    >
                      <Eye size={18} className="text-gray-600" />
                    </button>
                  )}
                  {onEdit && (
                    <button
                      onClick={() => onEdit(user)}
                      className="p-2 hover:bg-gray-100 rounded transition-colors"
                      title="Edit"
                    >
                      <Pencil size={18} className="text-gray-600" />
                    </button>
                  )}
                  {onDelete && (
                    <button
                      onClick={() => onDelete(user)}
                      className="p-2 hover:bg-red-50 rounded transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={18} className="text-red-600" />
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
