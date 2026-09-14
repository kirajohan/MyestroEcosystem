'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LogOut,
  Bell,
  Search,
  RefreshCw,
  MessageCircle,
  Command,
  Users,
  ClipboardCheck,
  Video,
  FileText,
  Megaphone,
} from 'lucide-react';
import toast from 'react-hot-toast';

// Sahifa nomlari
const pageNames: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/users': 'Foydalanuvchilar',
  '/inbox': 'Xabarlar',
  '/broadcast': 'Broadcast',
  '/content': 'Kontent',
  '/tests': 'Testlar',
  '/exam': 'Imtihonlar',
  '/exam/exams': 'Barcha imtihonlar',
  '/exam/bulk-import': 'Bulk Import',
  '/bot-texts': 'Bot matnlari',
};

// Qidiruv uchun sahifalar
const searchItems = [
  { title: 'Dashboard', path: '/dashboard', icon: ClipboardCheck, category: 'Sahifalar' },
  { title: 'Foydalanuvchilar', path: '/users', icon: Users, category: 'Sahifalar' },
  { title: 'Xabarlar', path: '/inbox', icon: MessageCircle, category: 'Sahifalar' },
  { title: 'Broadcast', path: '/broadcast', icon: Megaphone, category: 'Sahifalar' },
  { title: 'Kontent', path: '/content', icon: Video, category: 'Sahifalar' },
  { title: 'Testlar', path: '/tests', icon: FileText, category: 'Sahifalar' },
  { title: 'Imtihonlar', path: '/exam', icon: ClipboardCheck, category: 'Sahifalar' },
  { title: 'Bot matnlari', path: '/bot-texts', icon: FileText, category: 'Sahifalar' },
];

interface Notification {
  id: string;
  type: 'inbox' | 'broadcast' | 'exam' | 'system';
  title: string;
  message: string;
  time: string;
  read: boolean;
  path?: string;
}

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, logout } = useAuth();

  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const searchInputRef = useRef<HTMLInputElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);

  // Dinamik sarlavha
  const pageTitle =
    pageNames[pathname] ||
    (Object.keys(pageNames).find((key) => pathname?.startsWith(key))
      ? pageNames[Object.keys(pageNames).find((key) => pathname?.startsWith(key))!]
      : 'Dashboard');

  // ─── REFRESH ─────────────────────────────────────────────
  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await queryClient.invalidateQueries();
      router.refresh();
      toast.success('Yangilandi');
    } catch (error) {
      toast.error('Yangilashda xatolik');
    } finally {
      setTimeout(() => setIsRefreshing(false), 800);
    }
  }, [queryClient, router]);

  // ─── SEARCH KEYBOARD SHORTCUTS ───────────────────────────
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setShowSearch(true);
        setTimeout(() => searchInputRef.current?.focus(), 100);
      }
      if (e.key === 'Escape') {
        setShowSearch(false);
        setShowNotifications(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    if (showSearch) {
      setTimeout(() => searchInputRef.current?.focus(), 100);
    }
  }, [showSearch]);

  const filteredItems = searchItems.filter((item) =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSearchKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.min(prev + 1, filteredItems.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' && filteredItems[selectedIndex]) {
      e.preventDefault();
      router.push(filteredItems[selectedIndex].path);
      setShowSearch(false);
      setSearchQuery('');
      setSelectedIndex(0);
    }
  };

  useEffect(() => {
    setSelectedIndex(0);
  }, [searchQuery]);

  // ─── NOTIFICATIONS ───────────────────────────────────────
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (notificationRef.current && !notificationRef.current.contains(e.target as Node)) {
        setShowNotifications(false);
      }
    };

    if (showNotifications) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showNotifications]);

  useEffect(() => {
    setNotifications([
      {
        id: '1',
        type: 'inbox',
        title: 'Yangi xabar',
        message: 'John Doe sizga xabar yubordi',
        time: '2 daqiqa oldin',
        read: false,
        path: '/inbox',
      },
      {
        id: '2',
        type: 'broadcast',
        title: 'Broadcast tugadi',
        message: '150 ta foydalanuvchiga yuborildi',
        time: '1 soat oldin',
        read: false,
        path: '/broadcast',
      },
      {
        id: '3',
        type: 'exam',
        title: 'Yangi urinish',
        message: 'Ali B1 imtihonini boshladi',
        time: '3 soat oldin',
        read: true,
        path: '/exam',
      },
    ]);
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'inbox':
        return <MessageCircle className="w-4 h-4 text-blue-500" />;
      case 'broadcast':
        return <Megaphone className="w-4 h-4 text-orange-500" />;
      case 'exam':
        return <ClipboardCheck className="w-4 h-4 text-emerald-500" />;
      default:
        return <Bell className="w-4 h-4 text-slate-500" />;
    }
  };

  const markAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const handleNotificationClick = (notification: Notification) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === notification.id ? { ...n, read: true } : n))
    );
    if (notification.path) {
      router.push(notification.path);
    }
    setShowNotifications(false);
  };

  return (
    <>
      <header className="fixed top-0 left-0 right-0 md:left-60 h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 md:px-6 z-40">
        {/* Chap tomon */}
        <div className="flex items-center gap-3">
          <h2 className="text-lg md:text-xl font-bold text-slate-900 tracking-tight">
            {pageTitle}
          </h2>
        </div>

        {/* O'ng tomon */}
        <div className="flex items-center gap-1 md:gap-2">
          {/* Refresh */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition disabled:opacity-50"
            title="Yangilash"
          >
            <RefreshCw
              className={`w-5 h-5 ${isRefreshing ? 'animate-spin text-orange-500' : ''}`}
            />
          </motion.button>

          {/* Search (mobile) */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowSearch(true)}
            className="lg:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition"
            title="Qidirish"
          >
            <Search className="w-5 h-5" />
          </motion.button>

          {/* Search (desktop) */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            onClick={() => setShowSearch(true)}
            className="hidden lg:flex items-center gap-2 px-3 py-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg w-64 transition"
          >
            <Search className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-400 flex-1 text-left">Qidirish...</span>
            <kbd className="hidden xl:inline-flex items-center gap-0.5 text-xs text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
              <Command className="w-3 h-3" />K
            </kbd>
          </motion.button>

          {/* Notifications */}
          <div className="relative" ref={notificationRef}>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition"
              title="Bildirishnomalar"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute top-1 right-1 min-w-[18px] h-[18px] bg-orange-500 text-white text-xs font-bold rounded-full flex items-center justify-center px-1"
                >
                  {unreadCount > 9 ? '9+' : unreadCount}
                </motion.span>
              )}
            </motion.button>

            {/* Notifications Dropdown */}
            <AnimatePresence>
              {showNotifications && (
                <motion.div
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -10, scale: 0.95 }}
                  transition={{ duration: 0.15 }}
                  className="absolute right-0 mt-2 w-80 md:w-96 bg-white rounded-xl shadow-xl border border-slate-200 overflow-hidden"
                >
                  <div className="flex items-center justify-between p-4 border-b border-slate-100">
                    <h3 className="font-semibold text-slate-900">Bildirishnomalar</h3>
                    {unreadCount > 0 && (
                      <button
                        onClick={markAllRead}
                        className="text-xs text-orange-600 hover:text-orange-700 font-medium"
                      >
                        Hammasini oqilgan deb belgilash
                      </button>
                    )}
                  </div>

                  <div className="max-h-96 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="p-8 text-center">
                        <Bell className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                        <p className="text-sm text-slate-500">Bildirishnomalar yoq</p>
                      </div>
                    ) : (
                      <div className="divide-y divide-slate-100">
                        {notifications.map((notification) => (
                          <button
                            key={notification.id}
                            onClick={() => handleNotificationClick(notification)}
                            className={`w-full text-left p-4 hover:bg-slate-50 transition ${
                              !notification.read ? 'bg-orange-50/50' : ''
                            }`}
                          >
                            <div className="flex items-start gap-3">
                              <div className="flex-shrink-0 w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center">
                                {getNotificationIcon(notification.type)}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                  <p className="text-sm font-medium text-slate-900 truncate">
                                    {notification.title}
                                  </p>
                                  {!notification.read && (
                                    <span className="w-2 h-2 bg-orange-500 rounded-full flex-shrink-0" />
                                  )}
                                </div>
                                <p className="text-sm text-slate-600 mt-0.5 line-clamp-2">
                                  {notification.message}
                                </p>
                                <p className="text-xs text-slate-400 mt-1">{notification.time}</p>
                              </div>
                            </div>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Divider */}
          <div className="hidden sm:block w-px h-8 bg-slate-200 mx-1" />

          {/* User info */}
          <div className="hidden sm:flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center text-white font-semibold text-sm shadow-sm">
              {(user?.full_name || user?.email || 'A').charAt(0).toUpperCase()}
            </div>
            <div className="hidden md:block">
              <div className="text-sm font-semibold text-slate-900 leading-tight">
                {user?.full_name || user?.email || 'Admin'}
              </div>
              <div className="text-xs text-slate-500">Administrator</div>
            </div>
          </div>

          {/* Logout */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={logout}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition"
            title="Chiqish"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden md:inline">Chiqish</span>
          </motion.button>
        </div>
      </header>

      {/* ─── SEARCH MODAL ───────────────────────────────────── */}
      <AnimatePresence>
        {showSearch && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => {
                setShowSearch(false);
                setSearchQuery('');
              }}
              className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50"
            />

            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -20 }}
              transition={{ duration: 0.15 }}
              className="fixed top-[15%] left-1/2 -translate-x-1/2 w-full max-w-xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden z-50"
            >
              {/* Search Input */}
              <div className="flex items-center gap-3 p-4 border-b border-slate-200">
                <Search className="w-5 h-5 text-slate-400 flex-shrink-0" />
                <input
                  ref={searchInputRef}
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={handleSearchKeyDown}
                  placeholder="Sahifalar, foydalanuvchilar, testlar..."
                  className="flex-1 text-base text-slate-900 placeholder-slate-400 focus:outline-none"
                />
                <kbd className="hidden sm:inline-block text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded border border-slate-200">
                  ESC
                </kbd>
              </div>

              {/* Results */}
              <div className="max-h-96 overflow-y-auto p-2">
                {filteredItems.length === 0 ? (
                  <div className="p-8 text-center">
                    <Search className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                    <p className="text-sm text-slate-500">
                      {searchQuery} boyicha natija topilmadi
                    </p>
                  </div>
                ) : (
                  <>
                    {Object.entries(
                      filteredItems.reduce((acc, item) => {
                        if (!acc[item.category]) acc[item.category] = [];
                        acc[item.category].push(item);
                        return acc;
                      }, {} as Record<string, typeof filteredItems>)
                    ).map(([category, items]) => (
                      <div key={category}>
                        <div className="px-3 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                          {category}
                        </div>
                        {items.map((item) => {
                          const globalIdx = filteredItems.findIndex((i) => i.path === item.path);
                          const Icon = item.icon;
                          const isSelected = globalIdx === selectedIndex;

                          return (
                            <motion.button
                              key={item.path}
                              onClick={() => {
                                router.push(item.path);
                                setShowSearch(false);
                                setSearchQuery('');
                              }}
                              onMouseEnter={() => setSelectedIndex(globalIdx)}
                              whileHover={{ x: 4 }}
                              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition ${
                                isSelected
                                  ? 'bg-orange-50 text-orange-700'
                                  : 'text-slate-700 hover:bg-slate-50'
                              }`}
                            >
                              <div
                                className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                                  isSelected ? 'bg-orange-100' : 'bg-slate-100'
                                }`}
                              >
                                <Icon
                                  className={`w-4 h-4 ${
                                    isSelected ? 'text-orange-600' : 'text-slate-500'
                                  }`}
                                />
                              </div>
                              <span className="flex-1 text-left text-sm font-medium">
                                {item.title}
                              </span>
                              {isSelected && (
                                <kbd className="text-xs text-slate-400 bg-white px-2 py-0.5 rounded border border-slate-200">
                                  ↵
                                </kbd>
                              )}
                            </motion.button>
                          );
                        })}
                      </div>
                    ))}
                  </>
                )}
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between px-4 py-3 bg-slate-50 border-t border-slate-200 text-xs text-slate-500">
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <kbd className="bg-white px-1.5 py-0.5 rounded border border-slate-200">↑↓</kbd>
                    <span>Navigatsiya</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="bg-white px-1.5 py-0.5 rounded border border-slate-200">↵</kbd>
                    <span>Tanlash</span>
                  </span>
                </div>
                <span className="flex items-center gap-1">
                  <kbd className="bg-white px-1.5 py-0.5 rounded border border-slate-200">ESC</kbd>
                  <span>Yopish</span>
                </span>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}