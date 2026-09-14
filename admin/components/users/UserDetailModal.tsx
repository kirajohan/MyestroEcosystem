'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { UserResponse } from '@/lib/types';
import { toast } from 'sonner';
import { Eye, EyeOff, Save, X, Mail, Phone, Shield, Zap } from 'lucide-react';
import { useState } from 'react';
import { motion } from 'framer-motion';

const editUserSchema = z.object({
  full_name: z.string().min(1, 'Toliq ism majburiy'),
  email: z.string().email('Notoʻgʻri email').optional().or(z.literal('')),
  role: z.enum(['user', 'admin']),
  cefr_level: z.string(),
  target_level: z.string(),
  telegram_id: z.coerce.number().nullable().optional(),
  phone: z.string().optional(),
  password: z.string().min(6, 'Parol kamida 6 ta belgidan iborat bolishi kerak').optional().or(z.literal('')),
  is_active: z.boolean(),
  ai_enabled: z.boolean(),
});

type EditUserFormData = z.infer<typeof editUserSchema>;

interface UserEditFormProps {
  user: UserResponse;
  onSave: (data: EditUserFormData) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

interface UserDetailModalProps {
  user: UserResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

const CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
const ROLES = ['user', 'admin'];

export function UserDetailModal({ user, isOpen, onClose }: UserDetailModalProps) {
  if (!isOpen || !user) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
      className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4"
    >
      <motion.div
        initial={{ scale: 0.95, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-100 bg-gradient-to-r from-orange-50 to-orange-50">
          <h2 className="text-xl font-bold text-slate-900">Foydalanuvchi malumotlari</h2>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5 max-h-[70vh] overflow-y-auto">
          {/* Full Name */}
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Toliq Ism</p>
            <p className="text-base font-semibold text-slate-900">{user.full_name}</p>
          </div>

          {/* Email */}
          {user.email && (
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5" />
                Email
              </p>
              <a href={`mailto:${user.email}`} className="text-base text-orange-600 hover:text-orange-700 font-medium break-all">
                {user.email}
              </a>
            </div>
          )}

          {/* Phone */}
          {user.phone && (
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <Phone className="w-3.5 h-3.5" />
                Telefon
              </p>
              <p className="text-base font-medium text-slate-900">{user.phone}</p>
            </div>
          )}

          {/* Role */}
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5" />
              Rol
            </p>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-slate-100 rounded-lg">
              <span className={`w-2 h-2 rounded-full ${user.role === 'admin' ? 'bg-orange-600' : 'bg-emerald-600'}`}></span>
              <span className="text-sm font-semibold text-slate-900">
                {user.role === 'admin' ? 'Admin' : 'User'}
              </span>
            </div>
          </div>

          {/* CEFR Level */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">CEFR Level</p>
              <p className="text-lg font-bold text-slate-900 bg-blue-50 px-3 py-2 rounded-lg text-center">
                {user.cefr_level}
              </p>
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Target Level</p>
              <p className="text-lg font-bold text-slate-900 bg-purple-50 px-3 py-2 rounded-lg text-center">
                {user.target_level}
              </p>
            </div>
          </div>

          {/* Status Badges */}
          <div className="flex gap-2 flex-wrap pt-2">
            {user.is_active && (
              <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-100 rounded-full">
                <span className="w-2 h-2 bg-emerald-600 rounded-full"></span>
                <span className="text-xs font-semibold text-emerald-700">Faol</span>
              </div>
            )}
            {user.ai_enabled && (
              <div className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-100 rounded-full">
                <Zap className="w-3 h-3 text-blue-600" />
                <span className="text-xs font-semibold text-blue-700">AI Enabled</span>
              </div>
            )}
          </div>

          {/* Telegram ID */}
          {user.telegram_id && (
            <div className="pt-2 border-t border-slate-100">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Telegram ID</p>
              <p className="text-sm font-mono text-slate-700 bg-slate-100 px-3 py-2 rounded-lg">
                {user.telegram_id}
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex gap-2 p-6 border-t border-slate-100 bg-slate-50">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onClose}
            className="flex-1 px-4 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-xl font-medium text-sm hover:bg-slate-100 transition-all"
          >
            Yopish
          </motion.button>
        </div>
      </motion.div>
    </motion.div>
  );
}

export function UserEditForm({ user, onSave, onCancel, isLoading }: UserEditFormProps) {
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<EditUserFormData>({
    resolver: zodResolver(editUserSchema),
    defaultValues: {
      full_name: user.full_name,
      email: user.email || '',
      role: user.role,
      cefr_level: user.cefr_level,
      target_level: user.target_level,
      telegram_id: user.telegram_id,
      phone: user.phone || '',
      password: '',
      is_active: user.is_active,
      ai_enabled: user.ai_enabled,
    },
  });

  const onSubmit = async (data: EditUserFormData) => {
    try {
      const payload = { ...data };
      if (!payload.password) {
        delete (payload as any).password;
      }
      await onSave(payload as EditUserFormData);
      toast.success('Foydalanuvchi muvaffaqiyatli yangilandi');
      reset();
    } catch (error: any) {
      toast.error(error.message || 'Yangilashda xatolik');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
      {/* Full Name */}
      <div>
        <label className="block text-sm font-semibold text-slate-900 mb-1.5">
          Toliq Ism <span className="text-red-500"></span>
        </label>
        <input
          {...register('full_name')}
          className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all text-sm"
        />
        {errors.full_name && (
          <p className="text-xs text-red-600 mt-1">{errors.full_name.message}</p>
        )}
      </div>

      {/* Email */}
      <div>
        <label className="block text-sm font-semibold text-slate-900 mb-1.5">
          Email
        </label>
        <input
          type="email"
          {...register('email')}
          placeholder="user@example.com"
          className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all text-sm"
        />
        {errors.email && (
          <p className="text-xs text-red-600 mt-1">{errors.email.message}</p>
        )}
      </div>

      {/* Role & CEFR Level */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-semibold text-slate-900 mb-1.5">
            Rol
          </label>
          <select
            {...register('role')}
            className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all text-sm"
          >
            {ROLES.map((r) => (
              <option key={r} value={r}>
                {r === 'admin' ? 'Admin' : 'User'}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-900 mb-1.5">
            CEFR Level
          </label>
          <select
            {...register('cefr_level')}
            className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all text-sm"
          >
            {CEFR_LEVELS.map((level) => (
              <option key={level} value={level}>
                {level}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Target Level & Telegram ID */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-semibold text-slate-900 mb-1.5">
            Target Level
          </label>
          <select
            {...register('target_level')}
            className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all text-sm"
          >
            {CEFR_LEVELS.map((level) => (
              <option key={level} value={level}>
                {level}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-900 mb-1.5">
            Telegram ID
          </label>
          <input
            type="number"
            {...register('telegram_id')}
            placeholder="[REDACTED]"
            className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all text-sm"
          />
          {errors.telegram_id && (
            <p className="text-xs text-red-600 mt-1">{errors.telegram_id.message}</p>
          )}
        </div>
      </div>

      {/* Phone */}
      <div>
        <label className="block text-sm font-semibold text-slate-900 mb-1.5">
          Telefon raqam
        </label>
        <input
          type="tel"
          {...register('phone')}
          placeholder="+998901234567"
          className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all text-sm"
        />
        {errors.phone && (
          <p className="text-xs text-red-600 mt-1">{errors.phone.message}</p>
        )}
      </div>

      {/* Password with show/hide */}
      <div>
        <label className="block text-sm font-semibold text-slate-900 mb-1.5">
          Yangi parol
        </label>
        <div className="relative">
          <input
            type={showPassword ? 'text' : 'password'}
            {...register('password')}
            placeholder="Oʻzgartirmasangiz bosh qoldiring"
            className="w-full px-4 py-2.5 pr-11 border border-slate-200 rounded-xl bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all text-sm"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
          >
            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>
        {errors.password && (
          <p className="text-xs text-red-600 mt-1">{errors.password.message}</p>
        )}
        <p className="text-xs text-slate-500 mt-1">
          Parolni ozgartirmasangiz bu maydonni bosh qoldiring
        </p>
      </div>

      {/* Checkboxes */}
      <div className="flex items-center gap-6 pt-2">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            {...register('is_active')}
            className="w-4 h-4 text-orange-600 border-slate-300 rounded focus:ring-orange-500"
          />
          <span className="text-sm text-slate-700 font-medium">Active</span>
        </label>

        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            {...register('ai_enabled')}
            className="w-4 h-4 text-orange-600 border-slate-300 rounded focus:ring-orange-500"
          />
          <span className="text-sm text-slate-700 font-medium">AI Enabled</span>
        </label>
      </div>

      {/* Action buttons */}
      <div className="flex gap-2 pt-4 border-t border-slate-100">
        {onCancel && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-xl font-medium text-sm hover:bg-slate-50 disabled:opacity-50 transition-all"
          >
            <X className="w-4 h-4" />
            <span>Bekor qilish</span>
          </motion.button>
        )}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          type="submit"
          disabled={isLoading}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl font-medium text-sm hover:from-orange-600 hover:to-orange-700 disabled:opacity-50 transition-all shadow-lg shadow-orange-500/20"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Saqlanmoqda</span>
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              <span>Saqlash</span>
            </>
          )}
        </motion.button>
      </div>
    </form>
  );
}
