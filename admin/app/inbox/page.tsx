'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format, isToday, isYesterday } from 'date-fns';
import { uz } from 'date-fns/locale';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import { useInboxWebSocket } from '@/hooks/useInboxWebSocket';
import {
  MessageCircle,
  Send,
  Trash2,
  Check,
  CheckCheck,
  Search,
  Image as ImageIcon,
  Mic,
  File,
  Video,
  Smile,
  Loader2,
  RefreshCw,
  X,
  Menu,
  Inbox as InboxIcon,
} from 'lucide-react';
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
  updated_at?: string;
}

async function fetchWithAuth(url: string, token: string | null, options: RequestInit = {}) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const separator = url.includes('?') ? '&' : '?';
  const cacheBustUrl = `${url}${separator}_t=${Date.now()}`;

  const response = await fetch(cacheBustUrl, {
    ...options,
    headers,
    cache: 'no-store',
  });

  return response;
}

export default function InboxPage() {
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [replyText, setReplyText] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<'all' | 'unread' | 'replied'>('all');
  const [mobileShowChat, setMobileShowChat] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const { token, refreshToken, logout } = useAuth();

  useInboxWebSocket();

  const { data: messages = [], isLoading: isLoadingMessages, refetch, isFetching } = useQuery({
    queryKey: ['inbox-messages'],
    queryFn: async () => {
      console.log('📥 Fetching inbox messages...');

      const res = await fetchWithAuth('/api/inbox/messages', token);

      if (res.status === 401) {
        console.log('🔄 401 received, attempting refresh...');
        const newToken = await refreshToken();

        if (newToken) {
          console.log('✅ Token refreshed, retrying...');
          const retryRes = await fetchWithAuth('/api/inbox/messages', newToken);

          if (!retryRes.ok) {
            console.error('❌ Retry failed:', retryRes.status);
            throw new Error('Failed to fetch messages after refresh');
          }

          const data = await retryRes.json();
          console.log('✅ Fetched messages after refresh:', data.length);
          return data as Message[];
        } else {
          console.error('❌ Refresh failed, logging out');
          logout();
          throw new Error('Session expired');
        }
      }

      if (!res.ok) {
        console.error('❌ Fetch failed:', res.status);
        throw new Error('Failed to fetch messages');
      }

      const data = await res.json();
      console.log('✅ Fetched messages:', data.length);
      return data as Message[];
    },
    refetchInterval: 3000,
    refetchOnWindowFocus: true,
    staleTime: 0,
  });

  const conversations = React.useMemo(() => {
    const grouped = new Map<string, Message[]>();

    messages.forEach((msg) => {
      const userId = msg.user_telegram_id?.toString() || msg.user_id?.toString() || 'unknown';
      if (!grouped.has(userId)) {
        grouped.set(userId, []);
      }
      grouped.get(userId)!.push(msg);
    });

    return Array.from(grouped.entries())
      .map(([userId, msgs]) => ({
        userId,
        messages: msgs.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()),
        latestMessage: msgs[0],
        unreadCount: msgs.filter(m => !m.is_read).length,
        hasReplied: msgs.some(m => m.is_replied),
      }))
      .filter(conv => {
        if (filter === 'unread') return conv.unreadCount > 0;
        if (filter === 'replied') return conv.hasReplied;
        return true;
      })
      .filter(conv => {
        if (!searchQuery) return true;
        const name = conv.latestMessage.user_name || '';
        const text = conv.latestMessage.text || '';
        return name.toLowerCase().includes(searchQuery.toLowerCase()) ||
               text.toLowerCase().includes(searchQuery.toLowerCase());
      })
      .sort((a, b) => new Date(b.latestMessage.created_at).getTime() - new Date(a.latestMessage.created_at).getTime());
  }, [messages, filter, searchQuery]);

  const selectedConversation = conversations.find(c => c.userId === selectedUserId);

  const { mutate: sendReply, isPending: isSending } = useMutation({
    mutationFn: async (reply: string) => {
      if (!selectedConversation || !reply.trim()) {
        throw new Error('No conversation or empty reply');
      }

      const latestMsg = selectedConversation.latestMessage;
      console.log('📤 Sending reply to message:', latestMsg.id);

      let res = await fetchWithAuth(`/api/inbox/messages/${latestMsg.id}/reply`, token, {
        method: 'POST',
        body: JSON.stringify({ reply: reply.trim() }),
      });

      if (res.status === 401) {
        console.log('🔄 401 received on reply, attempting refresh...');
        const newToken = await refreshToken();

        if (newToken) {
          console.log('✅ Token refreshed, retrying reply...');
          res = await fetchWithAuth(`/api/inbox/messages/${latestMsg.id}/reply`, newToken, {
            method: 'POST',
            body: JSON.stringify({ reply: reply.trim() }),
          });
        } else {
          console.error('❌ Refresh failed on reply');
          throw new Error('Session expired');
        }
      }

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        console.error('❌ Reply failed:', errorData);
        throw new Error(errorData.detail || 'Failed to send reply');
      }

      const result = await res.json();
      console.log('✅ Reply sent:', result);
      return result;
    },
    onSuccess: () => {
      console.log('🎉 Reply mutation success');
      toast.success('Javob yuborildi!');
      setReplyText('');
      queryClient.invalidateQueries({ queryKey: ['inbox-messages'] });
      refetch();
    },
    onError: (error) => {
      console.error('❌ Reply mutation error:', error);
      toast.error(`Javob yuborilmadi: ${error.message}`);
    },
  });

  const { mutate: markRead } = useMutation({
    mutationFn: async (id: number) => {
      let res = await fetchWithAuth(`/api/inbox/messages/${id}/read`, token, {
        method: 'POST',
      });

      if (res.status === 401) {
        const newToken = await refreshToken();
        if (newToken) {
          res = await fetchWithAuth(`/api/inbox/messages/${id}/read`, newToken, {
            method: 'POST',
          });
        } else {
          throw new Error('Session expired');
        }
      }

      if (!res.ok) throw new Error('Failed to mark read');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inbox-messages'] });
    },
  });

  const { mutate: deleteMessage } = useMutation({
    mutationFn: async (id: number) => {
      let res = await fetchWithAuth(`/api/inbox/messages/${id}`, token, {
        method: 'DELETE',
      });

      if (res.status === 401) {
        const newToken = await refreshToken();
        if (newToken) {
          res = await fetchWithAuth(`/api/inbox/messages/${id}`, newToken, {
            method: 'DELETE',
          });
        } else {
          throw new Error('Session expired');
        }
      }

      if (!res.ok) throw new Error('Failed to delete');
      return res.json();
    },
    onSuccess: () => {
      toast.success('Xabar ochirildi');
      queryClient.invalidateQueries({ queryKey: ['inbox-messages'] });
    },
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [selectedUserId, selectedConversation?.messages.length]);

  useEffect(() => {
    if (selectedConversation) {
      selectedConversation.messages
        .filter(m => !m.is_read)
        .forEach(m => markRead(m.id));
    }
  }, [selectedUserId]);

  const handleSelectConversation = (userId: string) => {
    setSelectedUserId(userId);
    setMobileShowChat(true);
  };

  const handleBackToList = () => {
    setMobileShowChat(false);
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    if (isToday(date)) return format(date, 'HH:mm');
    if (isYesterday(date)) return 'Kecha';
    return format(date, 'dd MMM', { locale: uz });
  };

  const getContentIcon = (type: string) => {
    switch (type) {
      case 'photo': return <ImageIcon className="w-4 h-4" />;
      case 'voice': return <Mic className="w-4 h-4" />;
      case 'document': return <File className="w-4 h-4" />;
      case 'video': return <Video className="w-4 h-4" />;
      case 'sticker': return <Smile className="w-4 h-4" />;
      default: return null;
    }
  };

  const getAvatarColor = (userId: string) => {
    const colors = [
      'from-orange-500 to-orange-600',
      'from-blue-500 to-cyan-500',
      'from-emerald-500 to-green-500',
      'from-purple-500 to-pink-500',
      'from-indigo-500 to-purple-500',
    ];
    const index = parseInt(userId) % colors.length;
    return colors[index];
  };

  const totalUnread = conversations.reduce((sum, c) => sum + c.unreadCount, 0);

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gradient-to-br from-slate-50 via-white to-orange-50/30">
      {/* ─── Left Panel: Conversation List ─── */}
      <div
        className={`${
          mobileShowChat ? 'hidden md:flex' : 'flex'
        } w-full md:w-96 lg:w-[420px] border-r border-slate-200 bg-white flex-col flex-shrink-0`}
      >
        {/* Header */}
        <div className="p-4 border-b border-slate-200 bg-gradient-to-r from-orange-500 to-orange-600 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center shadow-sm">
                <InboxIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  Inbox
                  {totalUnread > 0 && (
                    <span className="px-2 py-0.5 bg-white text-orange-600 text-xs font-bold rounded-full">
                      {totalUnread}
                    </span>
                  )}
                </h2>
                <p className="text-xs text-white/80">
                  {conversations.length} ta suhbat
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {isFetching && (
                <RefreshCw className="w-4 h-4 text-white animate-spin" />
              )}
              <button
                onClick={() => refetch()}
                className="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition"
                title="Yangilash"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/60" />
            <input
              type="text"
              placeholder="Ism yoki xabar boyicha qidirish..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/40 text-sm transition-all"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-white/60 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="p-2 border-b border-slate-200 bg-slate-50">
          <div className="flex gap-1 bg-white rounded-xl p-1 border border-slate-200">
            {(['all', 'unread', 'replied'] as const).map((f) => {
              const isActive = filter === f;
              const label = f === 'all' ? 'Hammasi' : f === 'unread' ? 'Yangi' : 'Javob berilgan';
              const count = f === 'all'
                ? conversations.length
                : f === 'unread'
                ? conversations.filter(c => c.unreadCount > 0).length
                : conversations.filter(c => c.hasReplied).length;

              return (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-orange-500 to-orange-600 text-white shadow-sm shadow-orange-500/20'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {label}
                  {count > 0 && (
                    <span className={`ml-1.5 ${isActive ? 'text-white/80' : 'text-slate-400'}`}>
                      {count}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto">
          {isLoadingMessages ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
            </div>
          ) : conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-8">
              <div className="w-20 h-20 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <InboxIcon className="w-10 h-10 text-slate-300" />
              </div>
              <p className="text-slate-600 font-semibold">Xabar yoq</p>
              <p className="text-sm text-slate-400 mt-1">
                Hozircha hech qanday xabar kelmagan
              </p>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {conversations.map((conv, index) => {
                const latestMsg = conv.latestMessage;
                const isSelected = selectedUserId === conv.userId;
                const userName = latestMsg.user_name || `User ${conv.userId}`;

                return (
                  <motion.button
                    key={conv.userId}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.02 }}
                    onClick={() => handleSelectConversation(conv.userId)}
                    className={`w-full text-left p-4 transition-all border-l-4 ${
                      isSelected
                        ? 'bg-orange-50 border-l-orange-500'
                        : 'border-l-transparent hover:bg-slate-50 hover:border-l-orange-300'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={`flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br ${getAvatarColor(
                          conv.userId
                        )} flex items-center justify-center text-white font-bold shadow-md`}
                      >
                        {userName.charAt(0).toUpperCase()}
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <h3
                            className={`truncate ${
                              conv.unreadCount > 0
                                ? 'font-bold text-slate-900'
                                : 'font-semibold text-slate-700'
                            }`}
                          >
                            {userName}
                          </h3>
                          <span className="text-[10px] text-slate-500 flex-shrink-0 ml-2">
                            {formatDate(latestMsg.created_at)}
                          </span>
                        </div>

                        <div className="flex items-center gap-1.5">
                          <span className="text-slate-400 flex-shrink-0">
                            {getContentIcon(latestMsg.content_type)}
                          </span>
                          <p
                            className={`text-sm truncate ${
                              conv.unreadCount > 0 ? 'text-slate-900 font-medium' : 'text-slate-600'
                            }`}
                          >
                            {latestMsg.text || `${latestMsg.content_type}`}
                          </p>
                        </div>

                        <div className="flex items-center gap-2 mt-1.5">
                          {conv.unreadCount > 0 && (
                            <span className="px-2 py-0.5 bg-gradient-to-r from-orange-500 to-orange-600 text-white text-[10px] font-bold rounded-full shadow-sm shadow-orange-500/20">
                              {conv.unreadCount}
                            </span>
                          )}
                          {conv.hasReplied && (
                            <span className="flex items-center gap-1 text-[10px] text-emerald-600 font-medium">
                              <CheckCheck className="w-3 h-3" />
                              Javob berildi
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* ─── Right Panel: Chat ─── */}
      <div
        className={`${
          mobileShowChat ? 'flex' : 'hidden md:flex'
        } flex-1 flex-col bg-gradient-to-br from-slate-50 to-orange-50/20 min-w-0`}
      >
        {selectedConversation ? (
          <>
            {/* Chat Header */}
            <div className="px-4 md:px-6 py-4 bg-white border-b border-slate-200 shadow-sm flex-shrink-0">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <button
                    onClick={handleBackToList}
                    className="md:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition"
                  >
                    <Menu className="w-5 h-5" />
                  </button>
                  <div
                    className={`w-11 h-11 rounded-full bg-gradient-to-br ${getAvatarColor(
                      selectedConversation.userId
                    )} flex items-center justify-center text-white font-bold shadow-md flex-shrink-0`}
                  >
                    {selectedConversation.latestMessage.user_name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-bold text-slate-900 truncate">
                      {selectedConversation.latestMessage.user_name || `User ${selectedConversation.userId}`}
                    </h3>
                    <p className="text-xs text-slate-500">
                      {selectedConversation.messages.length} ta xabar
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
              <AnimatePresence>
                {selectedConversation.messages
                  .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
                  .map((msg) => (
                    <motion.div
                      key={msg.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="flex flex-col space-y-2"
                    >
                      {/* User message */}
                      <div className="flex items-end gap-2">
                        <div
                          className={`w-8 h-8 rounded-full bg-gradient-to-br ${getAvatarColor(
                            selectedConversation.userId
                          )} flex items-center justify-center text-white text-xs font-bold flex-shrink-0 shadow-sm`}
                        >
                          {msg.user_name?.charAt(0).toUpperCase() || 'U'}
                        </div>
                        <div className="max-w-[75%] md:max-w-[70%]">
                          <div className="bg-white rounded-2xl rounded-bl-md px-4 py-3 shadow-sm border border-slate-200">
                            {msg.text ? (
                              <p className="text-slate-800 text-sm whitespace-pre-wrap break-words">
                                {msg.text}
                              </p>
                            ) : (
                              <div className="flex items-center gap-2 text-slate-500">
                                {getContentIcon(msg.content_type)}
                                <span className="italic text-sm">
                                  {msg.content_type === 'photo' && 'Rasm yuborildi'}
                                  {msg.content_type === 'voice' && 'Ovozli xabar'}
                                  {msg.content_type === 'document' && 'Fayl yuborildi'}
                                  {msg.content_type === 'video' && 'Video yuborildi'}
                                  {msg.content_type === 'sticker' && 'Stiker'}
                                </span>
                              </div>
                            )}
                          </div>
                          <div className="flex items-center gap-2 mt-1 px-2">
                            <span className="text-[10px] text-slate-500">
                              {format(new Date(msg.created_at), 'HH:mm')}
                            </span>
                            {msg.is_read && <Check className="w-3 h-3 text-orange-500" />}
                          </div>
                        </div>
                      </div>

                      {/* Admin reply */}
                      {msg.admin_reply && (
                        <div className="flex items-end gap-2 justify-end">
                          <div className="max-w-[75%] md:max-w-[70%]">
                            <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-2xl rounded-br-md px-4 py-3 shadow-md shadow-orange-500/20">
                              <p className="whitespace-pre-wrap text-sm break-words">
                                {msg.admin_reply}
                              </p>
                            </div>
                            <div className="flex items-center gap-2 mt-1 px-2 justify-end">
                              <span className="text-[10px] text-slate-500">
                                {format(new Date(msg.created_at), 'HH:mm')}
                              </span>
                              <CheckCheck className="w-3 h-3 text-emerald-500" />
                            </div>
                          </div>
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 shadow-sm">
                            A
                          </div>
                        </div>
                      )}
                    </motion.div>
                  ))}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>

            {/* Reply Input */}
            <div className="p-3 md:p-4 bg-white border-t border-slate-200 flex-shrink-0">
              <div className="flex gap-2 items-end max-w-4xl mx-auto">
                <div className="flex-1 relative">
                  <textarea
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        if (replyText.trim() && !isSending) {
                          sendReply(replyText);
                        }
                      }
                    }}
                    placeholder="Javob yozing... (Enter - yuborish, Shift+Enter - yangi qator)"
                    className="w-full px-4 py-3 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 resize-none text-sm bg-slate-50 transition-all"
                    rows={2}
                    disabled={isSending}
                  />
                  {replyText.length > 0 && (
                    <span className="absolute bottom-2 right-3 text-[10px] text-slate-400">
                      {replyText.length}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => sendReply(replyText)}
                  disabled={!replyText.trim() || isSending}
                  className="px-5 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-2xl hover:shadow-lg hover:shadow-orange-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 font-medium flex-shrink-0"
                >
                  {isSending ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      <span className="hidden sm:inline">Yuborish</span>
                    </>
                  )}
                </button>
              </div>
              <p className="text-[10px] text-slate-400 text-center mt-2 hidden md:block">
                Enter - yuborish | Shift+Enter - yangi qator
              </p>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center max-w-sm">
              <div className="w-24 h-24 bg-gradient-to-br from-orange-100 to-orange-50 rounded-3xl flex items-center justify-center mx-auto mb-5 shadow-sm">
                <MessageCircle className="w-12 h-12 text-orange-500" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">
                Suhbatni tanlang
              </h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Chap tomondan foydalanuvchini tanlang yoki yangi xabar kelishini kuting
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}