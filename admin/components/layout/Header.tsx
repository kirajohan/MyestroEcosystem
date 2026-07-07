'use client';

import { usePathname } from 'next/navigation';
import { LogOut } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const pageNames: { [key: string]: string } = {
  '/dashboard': 'Dashboard',
  '/users': 'Users',
};

export function Header() {
  const pathname = usePathname();
  const { isLoggedIn, logout } = useAuth();

  const pageTitle = pageNames[pathname] || 'Dashboard';

  return (
    <header className="fixed top-0 left-0 right-0 md:left-60 h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 md:px-6 z-20">
      <h2 className="text-xl md:text-2xl font-semibold text-gray-800">{pageTitle}</h2>
      <div className="flex items-center gap-4">
        <span className="hidden sm:inline text-gray-600 text-sm md:text-base">Admin</span>
        <button
          onClick={logout}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="Logout"
        >
          <LogOut size={20} className="text-gray-600" />
        </button>
      </div>
    </header>
  );
}
