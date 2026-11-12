'use client';

import { useState } from 'react';
import { useSendMessage } from '@/hooks/useUsers';
import { toast } from 'sonner';
import { Send, MessageCircle, AlertCircle, CheckCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface DirectMessageProps {
  telegramId: number | null;
  userName: string;
}

export function DirectMessage({ telegramId, userName }: DirectMessageProps) {
  const [message, setMessage] = useState('');
  const sendMutation = useSendMessage();

  if (!telegramId) {
    return (
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-3"
      >
        <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-semibold text-amber-900">
            Telegram ID mavjud emas
          </p>
          <p className="text-xs text-amber-700 mt-0.5">
            Xabar yuborish uchun foydalanuvchida Telegram ID bolishi kerak
          </p>
        </div>
      </motion.div>
    );
  }

  const handleSend = async () => {
    if (!message.trim()) return;

    try {
      await sendMutation.mutateAsync({
        telegram_id: telegramId,
        text: message,
      });
      toast.success(`${userName} ga xabar yuborildi`);
      setMessage('');
    } catch (error: any) {
      toast.error(error.message || 'Xabar yuborilmadi');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="space-y-3">
      {/* Info banner */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-start gap-2.5 p-3 bg-blue-50 border border-blue-200 rounded-xl"
      >
        <MessageCircle className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-xs font-medium text-blue-900">
            Telegram orqali yuboriladi
          </p>
          <p className="text-xs text-blue-700 mt-0.5">
            Xabar Inbox tarixida saqlanadi va foydalanuvchiga Telegram bot orqali yetkaziladi
          </p>
        </div>
      </motion.div>

      {/* Textarea */}
      <div className="relative">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Xabar matnini kiriting..."
          rows={3}
          className="w-full px-4 py-3 border border-slate-200 rounded-xl bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all text-sm resize-none"
          disabled={sendMutation.isPending}
          maxLength={1000}
        />
        <div className="absolute bottom-3 right-3 flex items-center gap-2">
          <span className="text-xs text-slate-400">
            {message.length} / 1000
          </span>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex items-center justify-end gap-3">
        <p className="hidden sm:block text-xs text-slate-500 mr-auto">
          <kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded text-xs">
            Ctrl
          </kbd>
          {' + '}
          <kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded text-xs">
            Enter
          </kbd>
          {' yuborish uchun'}
        </p>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleSend}
          disabled={!message.trim() || message.length > 1000 || sendMutation.isPending}
          className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl font-medium text-sm hover:from-orange-600 hover:to-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-orange-500/20"
        >
          {sendMutation.isPending ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Yuborilmoqda...</span>
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span>Yuborish</span>
            </>
          )}
        </motion.button>
      </div>

      {/* Success message */}
      <AnimatePresence>
        {sendMutation.isSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-center gap-2 p-3 bg-emerald-50 border border-emerald-200 rounded-xl"
          >
            <CheckCircle className="w-4 h-4 text-emerald-600" />
            <p className="text-sm text-emerald-800">Xabar muvaffaqiyatli yuborildi!</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}