'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Bot, Sparkles, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import api from '@/lib/api';
import { toast } from 'sonner';

interface GlobalSetting {
  key: string;
  value: string;
  description?: string;
  updated_at?: string;
}

interface GlobalSwitchesData {
  BOT_ENABLED: GlobalSetting;
  AI_ENABLED: GlobalSetting;
  ai_global_enabled: GlobalSetting;
}

export function GlobalSwitches() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery<GlobalSwitchesData>({
    queryKey: ['global-settings'],
    queryFn: async () => {
      const response = await api.get('/settings/global');
      return response.data;
    },
    staleTime: 30000,
  });

  const botEnabled = data?.BOT_ENABLED?.value === 'true' || false;
  const aiEnabled = data?.AI_ENABLED?.value === 'true' || false;

  const toggleMutation = useMutation({
    mutationFn: async ({ key, value }: { key: string; value: boolean }) => {
      const response = await api.patch(`/settings/global/${key}`, {
        value: value ? 'true' : 'false',
      });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['global-settings'] });
      toast.success(
        data.setting_key === 'BOT_ENABLED'
          ? `Bot ${data.new_value === 'true' ? 'yoqildi' : 'o\'chirildi'}`
          : `AI ${data.new_value === 'true' ? 'yoqildi' : 'o\'chirildi'}`
      );
    },
    onError: (error: any) => {
      toast.error(error.message || 'Sozlamani o\'zgartirishda xatolik');
    },
  });

  const handleToggle = (key: string, currentValue: boolean) => {
    const newValue = !currentValue;
    const settingName = key === 'BOT_ENABLED' ? 'Bot' : 'AI';
    
    if (!newValue) {
      // O'chirishdan oldin ogohlantirish
      const confirmed = window.confirm(
        `${settingName}ni o'chirishni xohlaysizmi?\n\nBu barcha foydalanuvchilarga ta'sir qiladi.`
      );
      if (!confirmed) return;
    }

    toggleMutation.mutate({ key, value: newValue });
  };

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl border border-red-200 p-6 shadow-sm"
      >
        <div className="flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <p className="text-sm text-red-600">Sozlamalarni yuklashda xatolik</p>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-900">Global Boshqaruv</h3>
          <p className="text-xs text-slate-500 mt-1">Tizim sozlamalari</p>
        </div>
        {toggleMutation.isPending && (
          <Loader2 className="w-4 h-4 text-orange-500 animate-spin" />
        )}
      </div>

      <div className="space-y-4">
        {/* Bot Switch */}
        <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
              botEnabled ? 'bg-emerald-100' : 'bg-slate-200'
            }`}>
              <Bot className={`w-5 h-5 ${botEnabled ? 'text-emerald-600' : 'text-slate-500'}`} />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900">Bot Faolligi</p>
              <p className="text-xs text-slate-500">
                {botEnabled ? '✅ Bot ishlayapti' : '❌ Bot to\'xtatilgan'}
              </p>
            </div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={botEnabled}
              onChange={() => handleToggle('BOT_ENABLED', botEnabled)}
              disabled={toggleMutation.isPending || isLoading}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-orange-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-orange-500 peer-checked:to-orange-600"></div>
          </label>
        </div>

        {/* AI Switch */}
        <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
              aiEnabled ? 'bg-blue-100' : 'bg-slate-200'
            }`}>
              <Sparkles className={`w-5 h-5 ${aiEnabled ? 'text-blue-600' : 'text-slate-500'}`} />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900">AI Faolligi</p>
              <p className="text-xs text-slate-500">
                {aiEnabled ? '✅ AI suhbat ishlayapti' : '❌ AI to\'xtatilgan'}
              </p>
            </div>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={aiEnabled}
              onChange={() => handleToggle('AI_ENABLED', aiEnabled)}
              disabled={toggleMutation.isPending || isLoading}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-orange-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-orange-500 peer-checked:to-orange-600"></div>
          </label>
        </div>
      </div>

      {toggleMutation.isSuccess && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 flex items-center gap-2 text-sm text-emerald-600"
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>Sozlama muvaffaqiyatli yangilandi</span>
        </motion.div>
      )}
    </motion.div>
  );
}
