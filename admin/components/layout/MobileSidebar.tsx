'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Users,
  Video,
  FileText,
  Send,
  MessageSquare,
  ScrollText,
  Settings,
  Bot,
  FileQuestion,
  ClipboardCheck,
  Upload,
  Sparkles,
  Menu,
  X,
  LogOut,
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';

interface NavItem {
  label: string;
  href: string;
  icon: any;
  disabled?: boolean;  // ← Ixtiyoriy qilib belgilash
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const navSections = [
  {
    title: 'Asosiy',
    items: [
      { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
      { label: 'Foydalanuvchilar', href: '/users', icon: Users },
    ],
  },
  {
    title: 'Ta\'lim',
    items: [
      { label: 'Kontent', href: '/content', icon: Video },
      { label: 'Testlar', href: '/tests', icon: FileQuestion },
      { label: 'Imtihonlar', href: '/exam', icon: ClipboardCheck },
      { label: 'Bulk Import', href: '/exam/bulk-import', icon: Upload },
    ],
  },
  {
    title: 'Kommunikatsiya',
    items: [
      { label: 'Bot matnlari', href: '/bot-texts', icon: FileText },
      { label: 'Broadcast', href: '/broadcast', icon: Send },
      { label: 'Xabarlar', href: '/inbox', icon: MessageSquare },
    ],
  },
  {
    title: 'Tizim',
    items: [
      { label: 'Loglar', href: '#', icon: ScrollText, disabled: true },
      { label: 'Sozlamalar', href: '#', icon: Settings, disabled: true },
      { label: 'AI Chat', href: '#', icon: Bot, disabled: true },
    ],
  },
];

export function MobileSidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <>
      {/* Mobile menu button — Header'da ko'rinadi */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-3 left-3 z-50 md:hidden p-2.5 bg-white rounded-lg shadow-md border border-slate-200 hover:bg-slate-50 transition"
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div
              key="close"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <X size={22} className="text-slate-900" />
            </motion.div>
          ) : (
            <motion.div
              key="menu"
              initial={{ rotate: 90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: -90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <Menu size={22} className="text-slate-900" />
            </motion.div>
          )}
        </AnimatePresence>
      </button>

      {/* Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-30 bg-slate-900/60 backdrop-blur-sm md:hidden"
            onClick={() => setIsOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Mobile sidebar */}
      <AnimatePresence>
        {isOpen && (
          <motion.aside
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed left-0 top-0 h-screen w-72 bg-slate-900 flex flex-col z-40 md:hidden border-r border-slate-800"
          >
            {/* Logo + User */}
            <div className="p-5 border-b border-slate-800">
              <div className="flex items-center gap-2.5 mb-4">
                <div className="w-9 h-9 bg-gradient-to-br from-orange-400 to-orange-600 rounded-lg flex items-center justify-center shadow-lg shadow-orange-500/30">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-white">Myestro</h1>
                  <p className="text-xs text-slate-500 -mt-0.5">Admin Panel</p>
                </div>
              </div>

              {/* User info */}
              <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg">
                <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center text-white font-semibold">
                  {(user?.full_name || 'A').charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-white truncate">
                    {user?.full_name || 'Admin'}
                  </div>
                  <div className="text-xs text-slate-400 truncate">
                    {user?.email || 'admin@myestro.uz'}
                  </div>
                </div>
              </div>
            </div>

            {/* Nav */}
            <nav className="flex-1 overflow-y-auto px-3 py-4">
              {navSections.map((section) => (
                <div key={section.title} className="mb-5">
                  <h3 className="px-3 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    {section.title}
                  </h3>
                  <ul className="space-y-1">
                    {section.items.map((item) => {
                      const Icon = item.icon;
                      const isActive = 
                        pathname === item.href || 
                        (item.href !== '/dashboard' && pathname?.startsWith(item.href + '/'));
                      const isDisabled = 'disabled' in item ? item.disabled : false;

                      return (
                        <li key={item.label}>
                          <Link
                            href={isDisabled ? '#' : item.href}
                            onClick={() => {
                              if (!isDisabled) setIsOpen(false);
                            }}
                            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                              isDisabled
                                ? 'text-slate-600 cursor-not-allowed'
                                : isActive
                                  ? 'bg-orange-500 text-white shadow-lg shadow-orange-500/20'
                                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                            }`}
                          >
                            <Icon className="w-5 h-5 flex-shrink-0" />
                            <span className="text-sm font-medium flex-1">{item.label}</span>
                            {isDisabled && (
                              <span className="text-[10px] font-semibold text-slate-600 bg-slate-800 px-1.5 py-0.5 rounded">
                                SOON
                              </span>
                            )}
                          </Link>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ))}
            </nav>

            {/* Logout */}
            <div className="p-4 border-t border-slate-800">
              <button
                onClick={logout}
                className="w-full flex items-center gap-3 px-3 py-3 text-red-400 hover:bg-red-500/10 rounded-lg transition"
              >
                <LogOut className="w-5 h-5" />
                <span className="text-sm font-semibold">Chiqish</span>
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}