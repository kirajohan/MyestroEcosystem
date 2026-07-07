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
  LogOut,
  Menu,
  X,
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const navItems = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Users', href: '/users', icon: Users },
  { label: 'Content', href: '#', icon: Video, disabled: true },
  { label: 'Bot Texts', href: '#', icon: FileText, disabled: true },
  { label: 'Broadcast', href: '#', icon: Send, disabled: true },
  { label: 'Inbox', href: '#', icon: MessageSquare, disabled: true },
  { label: 'Logs', href: '#', icon: ScrollText, disabled: true },
  { label: 'Settings', href: '#', icon: Settings, disabled: true },
  { label: 'AI Chat', href: '#', icon: Bot, disabled: true },
];

export function MobileSidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const { logout } = useAuth();

  return (
    <>
      {/* Mobile menu button (visible on md and below) */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-40 md:hidden p-2 bg-white rounded-lg shadow hover:bg-gray-50"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Mobile sidebar overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black bg-opacity-50 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Mobile sidebar content */}
      <div
        className={`fixed left-0 top-0 h-screen w-60 bg-dark flex flex-col z-35 transform transition-transform duration-300 md:hidden ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Logo */}
        <div className="p-6 border-b border-stone-800">
          <h1 className="text-xl font-bold text-white">Myestro Admin</h1>
        </div>

        {/* Nav Items */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <ul className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              const isDisabled = item.disabled;

              return (
                <li key={item.label}>
                  <Link
                    href={item.href}
                    onClick={() => {
                      if (!isDisabled) setIsOpen(false);
                    }}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isDisabled
                        ? 'text-stone-600 cursor-not-allowed'
                        : isActive
                          ? 'bg-primary text-white'
                          : 'text-stone-300 hover:bg-stone-800'
                    }`}
                  >
                    <Icon size={20} />
                    <span className="text-sm font-medium">{item.label}</span>
                    {isDisabled && (
                      <span className="ml-auto text-xs text-stone-500">Soon</span>
                    )}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Logout Button */}
        <div className="p-4 border-t border-stone-800">
          <button
            onClick={() => {
              logout();
              setIsOpen(false);
            }}
            className="flex items-center gap-3 w-full px-4 py-3 text-stone-300 hover:bg-stone-800 rounded-lg transition-colors"
          >
            <LogOut size={20} />
            <span className="text-sm font-medium">Logout</span>
          </button>
        </div>
      </div>
    </>
  );
}
