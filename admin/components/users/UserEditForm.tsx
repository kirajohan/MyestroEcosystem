'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { UserResponse } from '@/lib/types';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { toast } from 'sonner';
import { Eye, EyeOff } from 'lucide-react';
import { useState } from 'react';

const editUserSchema = z.object({
  full_name: z.string().min(1, 'Toliq ism majburiy'),
  email: z.string().email('Noto\'g\'ri email'),
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
  isLoading?: boolean;
}

const CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];
const ROLES = ['user', 'admin'];

export function UserEditForm({ user, onSave, isLoading }: UserEditFormProps) {
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
      email: user.email,
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
      // Bo'sh password yuborilmaydi
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
      <Input
        label="Toliq Ism"
        {...register('full_name')}
        error={errors.full_name?.message}
      />

      <Input
        label="Email"
        type="email"
        {...register('email')}
        error={errors.email?.message}
      />

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Rol
          </label>
          <select
            {...register('role')}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          >
            {ROLES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            CEFR Level
          </label>
          <select
            {...register('cefr_level')}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          >
            {CEFR_LEVELS.map((level) => (
              <option key={level} value={level}>
                {level}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Level
          </label>
          <select
            {...register('target_level')}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          >
            {CEFR_LEVELS.map((level) => (
              <option key={level} value={level}>
                {level}
              </option>
            ))}
          </select>
        </div>

        <Input
          label="Telegram ID (ixtiyoriy)"
          type="number"
          {...register('telegram_id')}
          error={errors.telegram_id?.message}
        />
      </div>

      {/* Telefon raqam */}
      <Input
        label="Telefon raqam (ixtiyoriy)"
        type="tel"
        placeholder="+998901234567"
        {...register('phone')}
        error={errors.phone?.message}
      />

      {/* Parol */}
      <div className="relative">
        <Input
          label="Yangi parol (ixtiyoriy)"
          type={showPassword ? 'text' : 'password'}
          placeholder="O&apos;zgartirmasangiz bo&apos;sh qoldiring"
          {...register('password')}
          error={errors.password?.message}
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-3 top-[34px] text-gray-400 hover:text-gray-600"
        >
          {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
      <p className="text-xs text-gray-400 -mt-2">
        Parolni o&apos;zgartirmasangiz bu maydonni bo&apos;sh qoldiring.
      </p>

      <div className="flex items-center gap-6">
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" {...register('is_active')} />
          <span className="text-sm text-gray-700">Active</span>
        </label>

        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" {...register('ai_enabled')} />
          <span className="text-sm text-gray-700">AI Enabled</span>
        </label>
      </div>

      <Button type="submit" isLoading={isLoading}>
        Saqlash
      </Button>
    </form>
  );
}
