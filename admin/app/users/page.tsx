'use client';

import { useState, useMemo } from 'react';
import { useUsers, useUpdateUser, useDeleteUser } from '@/hooks/useUsers';
import { UserTable } from '@/components/users/UserTable';
import { UserEditForm } from '@/components/users/UserEditForm';
import { UserDetailModal } from '@/components/users/UserDetailModal';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { ErrorDisplay } from '@/components/common/ErrorDisplay';
import { EmptyState } from '@/components/common/EmptyState';
import { SkeletonTable } from '@/components/common/Skeleton';
import { Input } from '@/components/ui/Input';
import { UserResponse, UserUpdate } from '@/lib/types';
import { toast } from 'sonner';

const PAGE_SIZE = 50;

export default function UsersPage() {
  const [page, setPage] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState<UserResponse | null>(null);
  const [editingUser, setEditingUser] = useState<UserResponse | null>(null);
  const [deletingUser, setDeletingUser] = useState<UserResponse | null>(null);

  const { data, isLoading, error } = useUsers({
    skip: page * PAGE_SIZE,
    limit: PAGE_SIZE,
  });

  const updateMutation = useUpdateUser();
  const deleteMutation = useDeleteUser();

  // Client-side search filter
  const filteredUsers = useMemo(() => {
    if (!data?.data) return [];
    if (!searchTerm) return data.data;

    const term = searchTerm.toLowerCase();
    return data.data.filter(
      (user) =>
        user.full_name.toLowerCase().includes(term) ||
        (user.email?.toLowerCase().includes(term) ?? false) ||
        (user.telegram_username?.toLowerCase().includes(term) ?? false)
    );
  }, [data?.data, searchTerm]);

  const handleEdit = async (formData: UserUpdate) => {
    if (!editingUser) return;

    try {
      await updateMutation.mutateAsync({
        id: editingUser.id,
        data: formData,
      });
      setEditingUser(null);
    } catch (error: any) {
      toast.error(error.message || 'Failed to update user');
    }
  };

  const handleDelete = async () => {
    if (!deletingUser) return;

    try {
      await deleteMutation.mutateAsync(deletingUser.id);
      toast.success('User deleted successfully');
      setDeletingUser(null);
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete user');
    }
  };

  if (error) {
    return (
      <ErrorDisplay
        message="Failed to load users"
        onRetry={() => window.location.reload()}
      />
    );
  }

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0;

  return (
    <div className="space-y-6">
      {/* Search Input */}
      <Input
        placeholder="Search by name, email, or telegram username..."
        value={searchTerm}
        onChange={(e) => {
          setSearchTerm(e.target.value);
          setPage(0);
        }}
      />

      {/* Users Table or Loading/Empty */}
      {isLoading ? (
        <SkeletonTable />
      ) : filteredUsers.length === 0 ? (
        <EmptyState
          icon="users"
          title="Foydalanuvchilar topilmadi"
          description={searchTerm ? "Search natijasi bo'sh" : undefined}
        />
      ) : (
        <>
          <UserTable
            users={filteredUsers}
            isLoading={false}
            onView={setSelectedUser}
            onEdit={setEditingUser}
            onDelete={setDeletingUser}
          />

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Total: {data?.total} users
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(0, p - 1))}
                  disabled={page === 0}
                  className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 hover:bg-dark-100 transition-colors"
                >
                  Previous
                </button>
                <span className="px-4 py-2 text-sm text-gray-600">
                  Page {page + 1} of {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                  disabled={page >= totalPages - 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 hover:bg-dark-100 transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Detail Modal */}
      <UserDetailModal
        user={selectedUser}
        isOpen={!!selectedUser}
        onClose={() => setSelectedUser(null)}
      />

      {/* Edit Modal */}
      {editingUser && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-xl font-semibold text-gray-900">Edit User</h2>
              <button
                onClick={() => setEditingUser(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            <div className="p-6">
              <UserEditForm
                user={editingUser}
                onSave={handleEdit}
                isLoading={updateMutation.isPending}
              />
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirm Dialog */}
      <ConfirmDialog
        isOpen={!!deletingUser}
        title="Delete User"
        message={`Are you sure you want to delete ${deletingUser?.full_name}?`}
        onConfirm={handleDelete}
        onCancel={() => setDeletingUser(null)}
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
}
