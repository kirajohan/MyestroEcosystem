// components/dashboard/QuickActions.tsx
import { Plus, Upload, Users, FileText, Sparkles } from 'lucide-react';
import Link from 'next/link';

export function QuickActions() {
  const actions = [
    {
      label: 'Yangi imtihon',
      description: 'Imtihon yaratish',
      icon: Plus,
      href: '/exam/exams/new',
      color: 'bg-orange-500 hover:bg-orange-600',
    },
    {
      label: 'Bulk Import',
      description: 'JSON import qilish',
      icon: Upload,
      href: '/exam/bulk-import',
      color: 'bg-blue-500 hover:bg-blue-600',
    },
    {
      label: 'Foydalanuvchilar',
      description: 'Boshqaruv',
      icon: Users,
      href: '/users',
      color: 'bg-emerald-500 hover:bg-emerald-600',
    },
    {
      label: 'Kontent',
      description: 'Video va fayllar',
      icon: FileText,
      href: '/content',
      color: 'bg-purple-500 hover:bg-purple-600',
    },
  ];

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl p-6 text-white">
      <div className="flex items-center gap-2 mb-6">
        <Sparkles className="w-5 h-5 text-orange-400" />
        <h3 className="text-lg font-bold">Tezkor harakatlar</h3>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <Link
              key={action.label}
              href={action.href}
              className="group"
            >
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 hover:bg-white/20 transition-all duration-300 border border-white/10">
                <div className={`w-10 h-10 ${action.color} rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <p className="font-semibold text-sm mb-1">{action.label}</p>
                <p className="text-xs text-slate-400">{action.description}</p>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}