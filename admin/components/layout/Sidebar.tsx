'use client';

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
} from 'lucide-react';

// Aniq tip belgilash
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

// Bo'limlarga ajratilgan navigatsiya
const navSections: NavSection[] = [
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

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-900 flex flex-col z-40 border-r border-slate-800">
      {/* Logo */}
      <div className="p-6 border-b border-slate-800">
        <Link href="/dashboard" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 bg-gradient-to-br from-orange-400 to-orange-600 rounded-lg flex items-center justify-center shadow-lg shadow-orange-500/20 group-hover:shadow-orange-500/40 transition">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">Myestro</h1>
            <p className="text-xs text-slate-500 -mt-0.5">Admin Panel</p>
          </div>
        </Link>
      </div>

      {/* Nav Sections */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        {navSections.map((section) => (
          <div key={section.title} className="mb-6">
            <h3 className="px-3 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              {section.title}
            </h3>
            <ul className="space-y-1">
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = 
                  pathname === item.href || 
                  (item.href !== '/dashboard' && pathname?.startsWith(item.href + '/'));
                const isDisabled = item.disabled; 
                return (
                  <li key={item.label}>
                    <Link
                      href={isDisabled ? '#' : item.href}
                      onClick={(e) => isDisabled && e.preventDefault()}
                      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group ${
                        isDisabled
                          ? 'text-slate-600 cursor-not-allowed'
                          : isActive
                            ? 'bg-orange-500 text-white shadow-lg shadow-orange-500/20'
                            : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                      }`}
                    >
                      <Icon 
                        className={`w-5 h-5 flex-shrink-0 transition-colors ${
                          isActive ? 'text-white' : 'text-slate-500 group-hover:text-orange-400'
                        }`} 
                      />
                      <span className="text-sm font-medium flex-1">{item.label}</span>
                      {isDisabled && (
                        <span className="text-[10px] font-semibold text-slate-600 bg-slate-800 px-1.5 py-0.5 rounded">
                          SOON
                        </span>
                      )}
                      {isActive && !isDisabled && (
                        <span className="w-1.5 h-1.5 bg-white rounded-full" />
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-800">
        <div className="px-3 py-2 bg-slate-800/50 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Version</span>
            <span className="text-xs font-semibold text-orange-400">v2.1.0</span>
          </div>
        </div>
      </div>
    </aside>
  );
}