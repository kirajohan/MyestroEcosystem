'use client';

import { useState } from 'react';
import { useSendMessage } from '@/hooks/useUsers';
import { Button } from '@/components/ui/Button';
import { toast } from 'sonner';

interface DirectMessageProps {
  telegramId: number | null;
  userName: string;
}

export function DirectMessage({ telegramId, userName }: DirectMessageProps) {
  const [message, setMessage] = useState('');
  const sendMutation = useSendMessage();

  if (!telegramId) {
    return (
      <div className="p-4 bg-warning-50 border border-warning-200 rounded-lg">
        <p className="text-sm text-warning-800">
          ⚠️ Xabar yuborish uchun Telegram ID kerak
        </p>
      </div>
    );
  }

  const handleSend = async () => {
    if (!message.trim()) return;

    try {
      await sendMutation.mutateAsync({
        telegram_id: telegramId,
        text: message,
      });
      toast.success(`Xabar ${userName} ga yuborildi`);
      setMessage('');
    } catch (error: any) {
      toast.error(error.message || 'Xabar yuborilmadi');
    }
  };

  return (
    <div className="space-y-3">
      <div className="p-3 bg-primary-50 border border-primary-200 rounded text-sm text-primary-700">
        ℹ️ Xabar Telegram orqali yuboriladi. Tarix saqlanmaydi.
      </div>

      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Xabar matni..."
        rows={3}
        className="w-full px-4 py-2 border border-dark-200 rounded-lg bg-dark-50 focus:outline-none focus:ring-2 focus:ring-primary-600 resize-none"
        disabled={sendMutation.isPending}
      />

      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500">
          {message.length} / 1000
        </span>
        <Button
          onClick={handleSend}
          disabled={!message.trim() || message.length > 1000}
          isLoading={sendMutation.isPending}
          className="w-32"
        >
          Yuborish
        </Button>
      </div>
    </div>
  );
}
