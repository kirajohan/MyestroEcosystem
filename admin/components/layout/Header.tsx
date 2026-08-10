'use client';

import { usePathname } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { LogOut, User } from 'lucide-react';

const pageNames: { [key: string]: string } = {
  '/dashboard': 'Dashboard',
  '/users': 'Users',
  '/inbox': 'Inbox',
  '/broadcast': 'Broadcast',
  '/content': 'Content',
  '/tests': 'Tests',
};

export function Header() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const pageTitle = pageNames[pathname] || 'Dashboard';

  return (
    <header className="fixed top-0 left-0 right-0 md:left-60 h-16 bg-white border-b border-dark-200 shadow-sm flex items-center justify-between px-4 md:px-6 z-40">
      <h2 className="text-xl md:text-2xl font-semibold text-gray-800">{pageTitle}</h2>
      <div className="flex items-center gap-4">
        <div className="hidden sm:flex items-center gap-2 text-gray-600 text-sm md:text-base">
          <User className="w-4 h-4" />
          <span>{user?.full_name || user?.email || 'Admin'}</span>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-2 px-3 py-2 text-sm text-danger-700 hover:bg-danger-50 rounded-lg transition"
          title="Chiqish"
        >
          <LogOut className="w-4 h-4" />
          <span className="hidden sm:inline">Chiqish</span>
        </button>
      </div>
    </header>
  );
}