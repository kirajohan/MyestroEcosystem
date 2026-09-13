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
import { UserResponse, UserUpdate } from '@/lib/types';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import {
  Search,
  Users,
  UserCheck,
  ShieldCheck,
  Sparkles,
  Filter,
  RefreshCw,
  Plus,
  Download,
} from 'lucide-react';

const PAGE_SIZE = 50;

interface FilterChip {
  label: string;
  value: string;
  icon: any;
  color: string;
}

const FILTERS: FilterChip[] = [
  { label: 'Barchasi', value: 'all', icon: Users, color: 'slate' },
  { label: 'Faol', value: 'active', icon: UserCheck, color: 'emerald' },
  { label: 'Adminlar', value: 'admin', icon: ShieldCheck, color: 'orange' },
  { label: 'AI faol', value: 'ai_enabled', icon: Sparkles, color: 'blue' },
];

export default function UsersPage() {
  const [page, setPage] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  const [selectedUser, setSelectedUser] = useState<UserResponse | null>(null);
  const [editingUser, setEditingUser] = useState<UserResponse | null>(null);
  const [deletingUser, setDeletingUser] = useState<UserResponse | null>(null);

  const { data, isLoading, error, refetch } = useUsers({
    skip: page * PAGE_SIZE,
    limit: PAGE_SIZE,
  });

  const updateMutation = useUpdateUser();
  const deleteMutation = useDeleteUser();

  // Filter + Search logic
  const filteredUsers = useMemo(() => {
    if (!data?.data) return [];
    let result = data.data;

    // Filter bo'yicha
    if (activeFilter === 'active') {
      result = result.filter((u) => u.is_active);
    } else if (activeFilter === 'admin') {
      result = result.filter((u) => u.role === 'admin');
    } else if (activeFilter === 'ai_enabled') {
      result = result.filter((u) => u.ai_enabled);
    }

    // Search bo'yicha
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(
        (user) =>
          user.full_name?.toLowerCase().includes(term) ||
          (user.email?.toLowerCase().includes(term) ?? false) ||
          (user.telegram_username?.toLowerCase().includes(term) ?? false)
      );
    }

    return result;
  }, [data?.data, searchTerm, activeFilter]);

  // Stats (client-side)
  const stats = useMemo(() => {
    if (!data?.data) return { total: 0, active: 0, admins: 0, aiEnabled: 0 };
    return {
      total: data.total,
      active: data.data.filter((u) => u.is_active).length,
      admins: data.data.filter((u) => u.role === 'admin').length,
      aiEnabled: data.data.filter((u) => u.ai_enabled).length,
    };
  }, [data?.data]);

  const handleEdit = async (formData: UserUpdate) => {
    if (!editingUser) return;
    try {
      await updateMutation.mutateAsync({
        id: editingUser.id,
        data: formData,
      });
      toast.success('Foydalanuvchi muvaffaqiyatli yangilandi');
      setEditingUser(null);
    } catch (error: any) {
      toast.error(error.message || 'Yangilashda xatolik');
    }
  };

  const handleDelete = async () => {
    if (!deletingUser) return;
    try {
      await deleteMutation.mutateAsync(deletingUser.id);
      toast.success('Foydalanuvchi o\'chirildi');
      setDeletingUser(null);
    } catch (error: any) {
      toast.error(error.message || 'O\'chirishda xatolik');
    }
  };

  if (error) {
    return (
      <ErrorDisplay
        message="Foydalanuvchilarni yuklashda xatolik"
        onRetry={() => window.location.reload()}
      />
    );
  }

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Foydalanuvchilar</h1>
          <p className="text-slate-600 mt-1">
            Barcha royxatdan otgan foydalanuvchilarni boshqaring
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-slate-700 hover:bg-slate-50 transition font-medium text-sm"
          >
            <RefreshCw className="w-4 h-4" />
            Yangilash
          </button>
          <button
            onClick={() => {
              // TODO: CSV export
              toast.info('Tez orada qo\'shiladi');
            }}
            className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-slate-700 hover:bg-slate-50 transition font-medium text-sm"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
          <button
            onClick={() => {
              // TODO: Add new user
              toast.info('Tez orada qo\'shiladi');
            }}
            className="flex items-center gap-2 px-4 py-2.5 bg-orange-500 text-white rounded-xl hover:bg-orange-600 transition font-medium text-sm shadow-lg shadow-orange-500/20"
          >
            <Plus className="w-4 h-4" />
            Yangi user
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl border border-slate-200 p-5"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-slate-600" />
            </div>
            <span className="text-xs font-semibold text-slate-500 uppercase">Jami</span>
          </div>
          <p className="text-2xl font-bold text-slate-900">{stats.total}</p>
          <p className="text-xs text-slate-500 mt-1">Foydalanuvchilar</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="bg-white rounded-2xl border border-emerald-100 p-5"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="w-10 h-10 bg-emerald-50 rounded-lg flex items-center justify-center">
              <UserCheck className="w-5 h-5 text-emerald-600" />
            </div>
            <span className="text-xs font-semibold text-emerald-600 uppercase">Faol</span>
          </div>
          <p className="text-2xl font-bold text-slate-900">{stats.active}</p>
          <p className="text-xs text-slate-500 mt-1">Aktiv userlar</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl border border-orange-100 p-5"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="w-10 h-10 bg-orange-50 rounded-lg flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-orange-600" />
            </div>
            <span className="text-xs font-semibold text-orange-600 uppercase">Admin</span>
          </div>
          <p className="text-2xl font-bold text-slate-900">{stats.admins}</p>
          <p className="text-xs text-slate-500 mt-1">Administratorlar</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="bg-white rounded-2xl border border-blue-100 p-5"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-blue-600" />
            </div>
            <span className="text-xs font-semibold text-blue-600 uppercase">AI</span>
          </div>
          <p className="text-2xl font-bold text-slate-900">{stats.aiEnabled}</p>
          <p className="text-xs text-slate-500 mt-1">AI yoqilgan</p>
        </motion.div>
      </div>

      {/* Search + Filters */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4">
        <div className="flex flex-col md:flex-row gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
            <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Ism, email yoki telegram username bo'yicha qidirish..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setPage(0);
              }}
              className="w-full pl-11 pr-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
            />
          </div>

          {/* Filter chips */}
          <div className="flex flex-wrap gap-2">
            {FILTERS.map((filter) => {
              const Icon = filter.icon;
              const isActive = activeFilter === filter.value;
              return (
                <button
                  key={filter.value}
                  onClick={() => {
                    setActiveFilter(filter.value);
                    setPage(0);
                  }}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? filter.color === 'orange'
                        ? 'bg-orange-500 text-white shadow-lg shadow-orange-500/20'
                        : filter.color === 'emerald'
                        ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                        : filter.color === 'blue'
                        ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/20'
                        : 'bg-slate-900 text-white'
                      : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {filter.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Active filters summary */}
        {(searchTerm || activeFilter !== 'all') && (
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between">
            <p className="text-sm text-slate-600">
              Topildi: <span className="font-semibold text-slate-900">{filteredUsers.length}</span> foydalanuvchi
            </p>
            <button
              onClick={() => {
                setSearchTerm('');
                setActiveFilter('all');
              }}
              className="text-sm text-orange-600 hover:text-orange-700 font-medium"
            >
              Tozalash
            </button>
          </div>
        )}
      </div>

      {/* Users Table or Loading/Empty */}
      {isLoading ? (
        <SkeletonTable />
      ) : filteredUsers.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
          <EmptyState
            icon="users"
            title="Foydalanuvchilar topilmadi"
            description={
              searchTerm || activeFilter !== 'all'
                ? 'Qidiruv yoki filter shartlariga mos user topilmadi'
                : 'Hali hech kim ro\'yxatdan o\'tmagan'
            }
          />
        </div>
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
            <div className="bg-white rounded-2xl border border-slate-200 p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
              <p className="text-sm text-slate-600">
                Jami: <span className="font-semibold text-slate-900">{data?.total}</span> foydalanuvchi
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(0, p - 1))}
                  disabled={page === 0}
                  className="px-4 py-2 bg-white border border-slate-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors text-sm font-medium text-slate-700"
                >
                  ← Oldingi
                </button>
                <div className="flex items-center gap-1">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum: number;
                    if (totalPages <= 5) {
                      pageNum = i;
                    } else if (page < 3) {
                      pageNum = i;
                    } else if (page > totalPages - 4) {
                      pageNum = totalPages - 5 + i;
                    } else {
                      pageNum = page - 2 + i;
                    }
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setPage(pageNum)}
                        className={`w-9 h-9 rounded-lg text-sm font-medium transition-colors ${
                          page === pageNum
                            ? 'bg-orange-500 text-white shadow-md'
                            : 'text-slate-600 hover:bg-slate-100'
                        }`}
                      >
                        {pageNum + 1}
                      </button>
                    );
                  })}
                </div>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                  disabled={page >= totalPages - 1}
                  className="px-4 py-2 bg-white border border-slate-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 transition-colors text-sm font-medium text-slate-700"
                >
                  Keyingi →
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
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4"
        >
          <motion.div
            initial={{ scale: 0.95, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden"
          >
            <div className="flex items-center justify-between p-6 border-b border-slate-100">
              <h2 className="text-xl font-bold text-slate-900">Foydalanuvchini tahrirlash</h2>
              <button
                onClick={() => setEditingUser(null)}
                className="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition"
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
          </motion.div>
        </motion.div>
      )}

      {/* Delete Confirm Dialog */}
      <ConfirmDialog
        isOpen={!!deletingUser}
        title="Foydalanuvchini o'chirish"
        message={`${deletingUser?.full_name} foydalanuvchini o'chirishni xohlaysizmi? Bu amalni qaytarib bo'lmaydi.`}
        onConfirm={handleDelete}
        onCancel={() => setDeletingUser(null)}
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
}