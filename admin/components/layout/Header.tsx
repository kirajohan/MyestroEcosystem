'use client';

import { usePathname } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { LogOut, User, Bell, Search } from 'lucide-react';
import { motion } from 'framer-motion';

const pageNames: { [key: string]: string } = {
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

export function Header() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  
  // Dinamik sarlavha — ichki routelarni ham qamrab oladi
  const pageTitle = pageNames[pathname] || 
    Object.keys(pageNames).find(key => pathname?.startsWith(key)) 
      ? pageNames[Object.keys(pageNames).find(key => pathname?.startsWith(key))!] 
      : 'Dashboard';

  return (
    <header className="fixed top-0 left-0 right-0 md:left-64 h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 md:px-8 z-40">
      {/* Chap tomon: Sahifa nomi */}
      <div className="flex items-center gap-3">
        <h2 className="text-lg md:text-xl font-bold text-slate-900 tracking-tight">
          {pageTitle}
        </h2>
      </div>

      {/* O'ng tomon: Search + User + Logout */}
      <div className="flex items-center gap-2 md:gap-4">
        
        {/* Search (faqat desktop) */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg w-64">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Qidirish..."
            className="bg-transparent text-sm text-slate-700 placeholder-slate-400 focus:outline-none w-full"
          />
          <kbd className="hidden xl:inline-block text-xs text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
            ⌘K
          </kbd>
        </div>

        {/* Notifications (ixtiyoriy - kelajak uchun) */}
        <button className="relative p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-orange-500 rounded-full" />
        </button>

        {/* Divider */}
        <div className="hidden sm:block w-px h-8 bg-slate-200" />

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
  );
}