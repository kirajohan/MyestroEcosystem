'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { useAuth } from '@/context/AuthContext';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

export default function LoginPage() {
  const router = useRouter();
  const { isLoggedIn, login, isLoading, error: authError } = useAuth();
  const [formError, setFormError] = useState<string>('');

  const {
    register,
    handleSubmit,
  } = useForm<{ email: string; password: string }>({
    defaultValues: {
      email: '',
      password: '',
    },
  });

  // Auto redirect if already logged in
  useEffect(() => {
    if (isLoggedIn) {
      router.push('/dashboard');
    }
  }, [isLoggedIn, router]);

  const onSubmit = async (data: { email: string; password: string }) => {
    setFormError('');
    try {
      await login(data.email, data.password);
      router.push('/dashboard');
    } catch (err: any) {
      setFormError(authError || err?.message || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen bg-orange-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Myestro Admin</h1>
          <p className="text-gray-600 mt-2">Admin paneliga xush kelibsiz</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <Input
            label="Email"
            type="email"
            placeholder="admin@myestro.com"
            {...register('email')}
          />
          <Input
            label="Parol"
            type="password"
            placeholder="••••••••"
            {...register('password')}
          />

          {formError && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">{formError}</p>
            </div>
          )}

          <Button type="submit" isLoading={isLoading}>
            Kirish
          </Button>
        </form>
      </Card>
    </div>
  );
}
