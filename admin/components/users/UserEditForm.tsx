'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { UserResponse } from '@/lib/types';
import { toast } from 'sonner';
import { Eye, EyeOff, Save, X } from 'lucide-react';
import { useState } from 'react';
import { motion } from 'framer-motion';

const editUserSchema = z.object({
  full_name: z.string().min(1, 'Toliq ism majburiy'),
  email: z.string().email('Noto\'g\'ri email').optional().or(z.literal('')),
  role: z.enum(['user', 'admin']),
  cefr_level: z.string(),
  target_level: z.string(),
  telegram_id: z.coerce.number().nullable().optional(),
  phone: z.string().optional(),
  password: z.string().min(6, 'Parol kamida 6 ta belgidan iborat bo\'lishi kerak').optional().or(z.literal('')),
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

const CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
const ROLES = ['user', 'admin'];

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
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Full Name */}
      <div>
        <label className="block text-sm font-semibold text-slate-900 mb-1.5">
          Toliq Ism <span className="text-red-500">*</span>
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
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
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
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
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
            placeholder="123456789"
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
            placeholder="O'zgartirmasangiz bo'sh qoldiring"
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
      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 pt-2">
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
              <span>Saqlanmoqda...</span>
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