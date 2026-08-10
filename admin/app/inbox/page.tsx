'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { uz } from 'date-fns/locale';
import toast from 'react-hot-toast';

// Icons (lucide-react)
import { MessageCircle, Send, Trash2, Archive, CheckCircle, Clock, AlertCircle } from 'lucide-react';

interface Message {
  id: number;
  user_id: number;
  user_name: string;
  subject: string;
  user_message: string;
  admin_reply: string | null;
  status: 'new' | 'read' | 'replied' | 'closed';
  is_read: boolean;
  created_at: string;
  updated_at: string;
}

interface HistoryItem {
  id: number;
  sender_id: number;
  sender_name: string;
  message_text: string;
  message_type: 'user_message' | 'admin_reply';
  created_at: string;
}

interface MessageThread {
  message: Message;
  history: HistoryItem[];
}

export default function InboxPage() {
  const [selectedMessage, setSelectedMessage] = useState<number | null>(null);
  const [replyText, setReplyText] = useState('');
  const [filter, setFilter] = useState<'all' | 'new' | 'replied' | 'closed'>('all');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  // Fetch inbox messages
  const { data: messages = [], isLoading: isLoadingMessages, refetch } = useQuery({
    queryKey: ['inbox-messages', filter],
    queryFn: async () => {
      const url = `/api/inbox/messages${filter !== 'all' ? `?status=${filter}` : ''}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch messages');
      return res.json() as Promise<Message[]>;
    },
  });

  // Fetch selected message thread
  const { data: thread, isLoading: isLoadingThread } = useQuery({
    queryKey: ['inbox-thread', selectedMessage],
    queryFn: async () => {
      if (!selectedMessage) return null;
      const res = await fetch(`/api/inbox/messages/${selectedMessage}`);
      if (!res.ok) throw new Error('Failed to fetch thread');
      return res.json() as Promise<MessageThread>;
    },
    enabled: !!selectedMessage,
  });

  // Send reply mutation
  const { mutate: sendReply, isPending: isSending } = useMutation({
    mutationFn: async (reply: string) => {
      if (!selectedMessage || !reply.trim()) return;

      const res = await fetch(`/api/inbox/messages/${selectedMessage}/reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reply }),
      });

      if (!res.ok) throw new Error('Failed to send reply');
      return res.json();
    },
    onSuccess: () => {
      toast.success('✅ Javob yuborildi!');
      setReplyText('');
      refetch(); // Refresh list
      // Refetch thread to show updated status
      if (selectedMessage) {
        queryClient.invalidateQueries({ queryKey: ['inbox-thread', selectedMessage] });
      }
    },
    onError: () => {
      toast.error('❌ Javob yuborilmadi');
    },
  });

  // Delete message mutation
  const { mutate: deleteMessage } = useMutation({
    mutationFn: async (id: number) => {
      const res = await fetch(`/api/inbox/messages/${id}`, { method: 'DELETE' });
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

  // Update message status
  const { mutate: updateStatus } = useMutation({
    mutationFn: async (status: string) => {
      if (!selectedMessage) return;
      const res = await fetch(`/api/inbox/messages/${selectedMessage}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      if (!res.ok) throw new Error('Failed to update');
      return res.json();
    },
    onSuccess: () => {
      refetch();
    },
  });

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [thread]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'new':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'read':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'replied':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'closed':
        return <Archive className="w-4 h-4 text-gray-500" />;
      default:
        return null;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'new':
        return 'Yangi';
      case 'read':
        return 'Oqildi';
      case 'replied':
        return 'Javob Berildi';
      case 'closed':
        return 'Yopildi';
      default:
        return status;
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
            {(['all', 'new', 'replied', 'closed'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1 rounded text-sm ${
                  filter === f
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-dark-100'
                }`}
              >
                {f === 'all' ? 'Hamma' : getStatusLabel(f)}
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
                onClick={() => setSelectedMessage(msg.id)}
                className={`w-full text-left p-4 hover:bg-dark-100/50 transition ${
                  selectedMessage === msg.id ? 'bg-primary-50 border-l-4 border-primary' : ''
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-sm text-gray-900 truncate">
                      {msg.user_name}
                    </div>
                    <div className="text-xs text-gray-500 truncate">
                      {msg.subject || 'Mavzusiz'}
                    </div>
                    <div className="text-sm text-gray-700 truncate mt-1">
                      {msg.user_message}
                    </div>
                    <div className="text-xs text-gray-400 mt-2">
                      {format(new Date(msg.created_at), 'PPp', { locale: uz })}
                    </div>
                  </div>
                  <div className="flex-shrink-0">
                    {getStatusIcon(msg.status)}
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
        {selectedMessage && thread ? (
          <>
            {/* Header */}
            <div className="border-b p-4 flex items-center justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-bold">{thread.message.user_name}</h3>
                <p className="text-sm text-gray-500">{thread.message.subject}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1 text-sm px-3 py-1 bg-gray-100 rounded">
                  {getStatusIcon(thread.message.status)}
                  {getStatusLabel(thread.message.status)}
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

            {/* Chat History */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {/* Initial message */}
              <div className="bg-gray-100 rounded-lg p-4">
                <div className="text-xs text-gray-500 mb-2">
                  {format(new Date(thread.message.created_at), 'PPp', { locale: uz })}
                </div>
                <div className="text-gray-800">{thread.message.user_message}</div>
              </div>

              {/* History */}
              {thread.history.map((item) => (
                <div
                  key={item.id}
                  className={`rounded-lg p-4 ${
                    item.message_type === 'user_message'
                      ? 'bg-gray-100 text-gray-800'
                      : 'bg-primary-100 text-primary-900'
                  }`}
                >
                  <div className="text-xs text-gray-600 mb-1 font-semibold">
                    {item.sender_name}
                  </div>
                  <div className="text-xs text-gray-500 mb-2">
                    {format(new Date(item.created_at), 'PPp', { locale: uz })}
                  </div>
                  <div>{item.message_text}</div>
                </div>
              ))}

              <div ref={messagesEndRef} />
            </div>

            {/* Reply Box */}
            {thread.message.status !== 'closed' && (
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

                {/* Status Options */}
                {thread.message.status === 'replied' && (
                  <div className="mt-3 flex gap-2">
                    <button
                      onClick={() => updateStatus('closed')}
                      className="text-sm px-3 py-2 bg-gray-200 hover:bg-gray-300 rounded"
                    >
                      ✓ Yopish
                    </button>
                  </div>
                )}
              </div>
            )}

            {thread.message.status === 'closed' && (
              <div className="border-t p-4 bg-gray-50 text-center text-gray-500">
                🔒 Bu xabar yopilgan
              </div>
            )}
          </>
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
