"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getMe, logout } from "@/lib/api";

interface UserInfo {
  id: number;
  full_name: string | null;
  cefr_level: string | null;
  role: string;
}

const SECTIONS = [
  { key: "full", title: "Full Exam", desc: "To'liq imtihon sikli", icon: "🎯", color: "bg-indigo-500" },
  { key: "listening", title: "Listening", desc: "Tinglab tushunish", icon: "🎧", color: "bg-blue-500" },
  { key: "reading", title: "Reading", desc: "O'qib tushunish", icon: "📖", color: "bg-emerald-500" },
  { key: "writing", title: "Writing", desc: "Yozma ish", icon: "✍️", color: "bg-amber-500" },
  { key: "speaking", title: "Speaking", desc: "Og'zaki nutq", icon: "🎤", color: "bg-rose-500" },
];

export default function CabinetPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      const res = await getMe();
      if (res.ok && res.data) {
        setUser(res.data as UserInfo);
      } else {
        router.push("/login");
      }
      setLoading(false);
    }
    loadUser();
  }, [router]);

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <p className="text-slate-500">Yuklanmoqda...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-primary-700">Maestro Exam</h1>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="font-medium">{user?.full_name || "Foydalanuvchi"}</p>
              <p className="text-sm text-slate-500">
                Daraja: {user?.cefr_level || "—"}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="text-sm text-slate-600 hover:text-red-600 transition-colors"
            >
              Chiqish
            </button>
          </div>
        </div>
      </header>

      {/* Sections */}
      <div className="max-w-6xl mx-auto p-6">
        <h2 className="text-2xl font-bold mb-6">Imtihon bo'limlari</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {SECTIONS.map((section) => (
            <button
              key={section.key}
              onClick={() => router.push(`/exams?type=${section.key}`)}
              className="card text-left hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
            >
              <div className={`w-12 h-12 ${section.color} rounded-lg flex items-center justify-center text-2xl mb-4`}>
                {section.icon}
              </div>
              <h3 className="text-lg font-semibold">{section.title}</h3>
              <p className="text-sm text-slate-500 mt-1">{section.desc}</p>
            </button>
          ))}
        </div>
      </div>
    </main>
  );
}