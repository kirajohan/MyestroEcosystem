"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface ExamStats {
  total_exams: number;
  total_attempts: number;
  completed_attempts: number;
  average_score: number;
}

export default function ExamDashboardPage() {
  const [stats, setStats] = useState<ExamStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        // Backend API'dan statistika olish (hozircha mock data)
        // const res = await fetch("http://localhost:8002/api/v2/exam/admin/stats", {
        //   credentials: "include",
        // });
        // if (res.ok) {
        //   const data = await res.json();
        //   setStats(data);
        // }
        
        // Mock data (backend API tayyor bo'lguncha)
        setStats({
          total_exams: 0,
          total_attempts: 0,
          completed_attempts: 0,
          average_score: 0,
        });
      } catch (error) {
        console.error("Stats yuklanmadi:", error);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  if (loading) {
    return <div className="p-6">Yuklanmoqda...</div>;
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Exam Dashboard</h1>
        <p className="text-gray-600 mt-1">Imtihonlar statistikasi</p>
      </div>

      {/* Statistika kartochkalari */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600">Jami examlar</div>
          <div className="text-3xl font-bold text-blue-600 mt-2">
            {stats?.total_exams || 0}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600">Jami urinishlar</div>
          <div className="text-3xl font-bold text-green-600 mt-2">
            {stats?.total_attempts || 0}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600">Yakunlangan</div>
          <div className="text-3xl font-bold text-purple-600 mt-2">
            {stats?.completed_attempts || 0}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600">O&rsquo;rtacha ball</div>
          <div className="text-3xl font-bold text-orange-600 mt-2">
            {stats?.average_score?.toFixed(1) || 0}%
          </div>
        </div>
      </div>

      {/* Tezkor havolalar */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Tezkor havolalar</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/exam/exams"
            className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="text-2xl mr-3">📝</div>
            <div>
              <div className="font-semibold">Exam&rsquo;lar</div>
              <div className="text-sm text-gray-600">Yaratish va boshqarish</div>
            </div>
          </Link>

          <Link
            href="/exam/attempts"
            className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="text-2xl mr-3">📊</div>
            <div>
              <div className="font-semibold">Urinishlar</div>
              <div className="text-sm text-gray-600">Foydalanuvchi natijalari</div>
            </div>
          </Link>

          <Link
            href="/exam/create"
            className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="text-2xl mr-3">➕</div>
            <div>
              <div className="font-semibold">Yangi Exam</div>
              <div className="text-sm text-gray-600">Imtihon yaratish</div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
