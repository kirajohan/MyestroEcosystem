'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { uz } from 'date-fns/locale';
import toast from 'react-hot-toast';

// Icons (lucide-react)
import { MessageCircle, Send, Trash2, Archive, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

interface Message {
  id: number;
  user_id: number | null;
  user_telegram_id: number | null;
  user_name: string | null;
  content_type: string;
  text: string | null;
  file_id: string | null;
  is_read: boolean;
  is_replied: boolean;
  admin_reply: string | null;
  created_at: string;
}

export default function InboxPage() {
  const [selectedMessage, setSelectedMessage] = useState<number | null>(null);
  const [replyText, setReplyText] = useState('');
  const [filter, setFilter] = useState<'all' | 'unread' | 'replied'>('all');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const { token } = useAuth();

  // Fetch inbox messages
  const { data: messages = [], isLoading: isLoadingMessages, refetch } = useQuery({
    queryKey: ['inbox-messages', filter],
    queryFn: async () => {
      const url = `/api/inbox/messages${filter !== 'all' ? `?is_read=${filter === 'unread' ? 'false' : 'true'}` : ''}`;
      const res = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error('Failed to fetch messages');
      return res.json() as Promise<Message[]>;
    },
  });

  // Send reply mutation
  const { mutate: sendReply, isPending: isSending } = useMutation({
    mutationFn: async (reply: string) => {
      if (!selectedMessage || !reply.trim()) return;

      const res = await fetch(`/api/inbox/messages/${selectedMessage}/reply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ reply }),
      });

      if (!res.ok) throw new Error('Failed to send reply');
      return res.json();
    },
    onSuccess: () => {
      toast.success('✅ Javob yuborildi!');
      setReplyText('');
      refetch(); // Refresh list
    },
    onError: () => {
      toast.error('❌ Javob yuborilmadi');
    },
  });

  // Delete message mutation
  const { mutate: deleteMessage } = useMutation({
    mutationFn: async (id: number) => {
      const res = await fetch(`/api/inbox/messages/${id}`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error('Failed to delete');
      return res.json();
    },
    onSuccess: () => {
      toast.success('🗑️ Xabar ochirildi');
      setSelectedMessage(null);
      refetch();
    },
    onError: () => {
      toast.error('❌ Ochirilmadi');
    },
  });

  // Mark as read mutation
  const { mutate: markRead } = useMutation({
    mutationFn: async (id: number) => {
      const res = await fetch(`/api/inbox/messages/${id}/read`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error('Failed to mark read');
      return res.json();
    },
    onSuccess: () => {
      refetch();
    },
  });

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [selectedMessage]);

  const getStatusIcon = (msg: Message) => {
    if (msg.is_replied) return <CheckCircle className="w-4 h-4 text-green-500" />;
    if (msg.is_read) return <Clock className="w-4 h-4 text-yellow-500" />;
    return <AlertCircle className="w-4 h-4 text-red-500" />;
  };

  const getStatusLabel = (msg: Message) => {
    if (msg.is_replied) return 'Javob Berildi';
    if (msg.is_read) return 'Oqildi';
    return 'Yangi';
  };

  const getContentPreview = (msg: Message) => {
    if (msg.text) return msg.text;
    switch (msg.content_type) {
      case 'photo': return '📷 Rasm';
      case 'voice': return '🎤 Ovozli xabar';
      case 'document': return '📄 Fayl';
      case 'video': return '🎬 Video';
      case 'sticker': return '😀 Stiker';
      default: return 'Xabar';
    }
  };

  return (
    <div className="flex h-full bg-gray-50">
      {/* Messages List */}
      <div className="w-1/3 border-r bg-white overflow-y-auto">
        <div className="sticky top-0 bg-white border-b p-4 shadow-sm">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <MessageCircle className="w-5 h-5 text-primary" />
            Inbox
          </h2>

          {/* Filter */}
          <div className="flex gap-2 flex-wrap">
            {(['all', 'unread', 'replied'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1 rounded text-sm ${
                  filter === f
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-dark-100'
                }`}
              >
                {f === 'all' ? 'Hamma' : f === 'unread' ? 'Yangi' : 'Javob Berilgan'}
              </button>
            ))}
          </div>
        </div>

        {/* Messages */}
        {isLoadingMessages ? (
          <div className="p-4 text-center text-gray-500">Yuklanyotgan...</div>
        ) : messages.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <MessageCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>Xabar yoq</p>
          </div>
        ) : (
          <div className="divide-y">
            {messages.map((msg) => (
              <button
                key={msg.id}
                onClick={() => {
                  setSelectedMessage(msg.id);
                  if (!msg.is_read) markRead(msg.id);
                }}
                className={`w-full text-left p-4 hover:bg-dark-100/50 transition ${
                  selectedMessage === msg.id ? 'bg-primary-50 border-l-4 border-primary' : ''
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-sm text-gray-900 truncate">
                      {msg.user_name || `User ${msg.user_telegram_id || ''}`}
                    </div>
                    <div className="text-sm text-gray-700 truncate mt-1">
                      {getContentPreview(msg)}
                    </div>
                    <div className="text-xs text-gray-400 mt-2">
                      {format(new Date(msg.created_at), 'PPp', { locale: uz })}
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    {getStatusIcon(msg)}
                  </div>
                </div>

                {!msg.is_read && (
                  <div className="mt-2 w-2 h-2 bg-red-500 rounded-full"></div>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Message Detail & Reply */}
      <div className="flex-1 flex flex-col bg-white">
        {selectedMessage ? (
          (() => {
            const msg = messages.find(m => m.id === selectedMessage);
            if (!msg) return (
              <div className="flex-1 flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <MessageCircle className="w-16 h-16 mx-auto mb-4 opacity-20" />
                  <p>Xabar topilmadi</p>
                </div>
              </div>
            );
            return (
              <>
                {/* Header */}
                <div className="border-b p-4 flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold">{msg.user_name || `User ${msg.user_telegram_id || ''}`}</h3>
                    <p className="text-sm text-gray-500">{getContentPreview(msg)}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="flex items-center gap-1 text-sm px-3 py-1 bg-gray-100 rounded">
                      {getStatusIcon(msg)}
                      {getStatusLabel(msg)}
                    </span>
                    <button
                      onClick={() => deleteMessage(selectedMessage)}
                      className="p-2 hover:bg-gray-100 rounded"
                      title="Ochirish"
                    >
                      <Trash2 className="w-5 h-5 text-red-500" />
                    </button>
                  </div>
                </div>

                {/* Message Content */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  <div className="bg-gray-100 rounded-lg p-4">
                    <div className="text-xs text-gray-500 mb-2">
                      {format(new Date(msg.created_at), 'PPp', { locale: uz })}
                    </div>
                    {msg.text ? (
                      <div className="text-gray-800">{msg.text}</div>
                    ) : (
                      <div className="text-gray-500 italic">
                        {msg.content_type === 'photo' && '📷 Rasm yuborilgan'}
                        {msg.content_type === 'voice' && '🎤 Ovozli xabar yuborilgan'}
                        {msg.content_type === 'document' && '📄 Fayl yuborilgan'}
                        {msg.content_type === 'video' && '🎬 Video yuborilgan'}
                        {msg.content_type === 'sticker' && '😀 Stiker yuborilgan'}
                      </div>
                    )}
                  </div>

                  {msg.admin_reply && (
                    <div className="bg-primary-100 text-primary-900 rounded-lg p-4">
                      <div className="text-xs text-gray-600 mb-1 font-semibold">Admin javobi</div>
                      <div>{msg.admin_reply}</div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Reply Box */}
                <div className="border-t p-4 bg-gray-50">
                  <div className="flex gap-2">
                    <textarea
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      placeholder="Javob yozing..."
                      className="flex-1 p-3 border rounded resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                      rows={3}
                      disabled={isSending}
                    />
                    <button
                      onClick={() => sendReply(replyText)}
                      disabled={!replyText.trim() || isSending}
                      className="px-4 py-3 bg-primary text-white rounded hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      <Send className="w-4 h-4" />
                      {isSending ? 'Yuborilmoqda...' : 'Yuborish'}
                    </button>
                  </div>
                </div>
              </>
            );
          })()
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <MessageCircle className="w-16 h-16 mx-auto mb-4 opacity-20" />
              <p>Xabar tanlang</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}