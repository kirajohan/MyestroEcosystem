"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

interface Exam {
  id: number;
  code: string;
  title: string;
  description: string | null;
  exam_type: string;
  cefr_level: string | null;
  time_limit_sec: number;
  is_published: boolean;
}

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

const TYPE_ICONS: Record<string, string> = {
  full: "🎯",
  listening: "🎧",
  reading: "📖",
  writing: "✍️",
  speaking: "🎤",
};

export default function ExamsListPage() {
  const router = useRouter();
  const { token } = useAuth();

  const [exams, setExams] = useState<Exam[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadExams() {
      setLoading(true);
      setError("");

      try {
        const res = await fetch(
          `${API_URL}/api/v2/exam/admin/exams`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();

        setExams(data.items || []);
        setTotal(data.total || 0);
      } catch (err) {
        console.error("Examlar yuklanmadi:", err);
        setError(
          "Examlar yuklanmadi. Token yoki backendni tekshiring."
        );
      } finally {
        setLoading(false);
      }
    }

    if (token) {
      loadExams();
    }
  }, [token]);

  async function handleDelete(examId: number) {
    const confirmed = confirm(
      "Bu examni ochirishni xohlaysizmi? Bu amalni qaytarib bolmaydi!"
    );

    if (!confirmed) {
      return;
    }

    try {
      const res = await fetch(
        `${API_URL}/api/v2/exam/admin/exams/${examId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (res.ok) {
        setExams((currentExams) =>
          currentExams.filter((exam) => exam.id !== examId)
        );

        setTotal((currentTotal) => currentTotal - 1);
      } else {
        alert("Ochirishda xatolik yuz berdi");
      }
    } catch (err) {
      console.error("Ochirish xatosi:", err);
      alert("Ochirishda xatolik yuz berdi");
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        Yuklanmoqda...
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">
            Examlar
          </h1>

          <p className="text-gray-600 mt-1">
            Jami: {total} ta
          </p>
        </div>

        <Link
          href="/exam/create"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          + Yangi Exam
        </Link>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-4">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Turi
              </th>

              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Nomi
              </th>

              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Kod
              </th>

              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Daraja
              </th>

              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Vaqt
              </th>

              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>

              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Amallar
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-200">
            {exams.map((exam) => (
              <tr
                key={exam.id}
                className="hover:bg-gray-50"
              >
                {/* Type */}
                <td className="px-6 py-4 text-xl">
                  {TYPE_ICONS[exam.exam_type] || "📝"}
                </td>

                {/* Title */}
                <td className="px-6 py-4 font-medium">
                  {exam.title}
                </td>

                {/* Code */}
                <td className="px-6 py-4 text-sm font-mono text-gray-600">
                  {exam.code}
                </td>

                {/* CEFR */}
                <td className="px-6 py-4">
                  {exam.cefr_level ? (
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-semibold">
                      {exam.cefr_level}
                    </span>
                  ) : (
                    "—"
                  )}
                </td>

                {/* Time */}
                <td className="px-6 py-4 text-sm">
                  {Math.floor(
                    exam.time_limit_sec / 60
                  )}{" "}
                  daq
                </td>

                {/* Status */}
                <td className="px-6 py-4">
                  {exam.is_published ? (
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                      Published
                    </span>
                  ) : (
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                      Draft
                    </span>
                  )}
                </td>

                {/* Actions */}
                <td className="px-6 py-4 text-sm">
                  <button
                    type="button"
                    onClick={() =>
                      router.push(
                        `/exam/exams/${exam.id}`
                      )
                    }
                    className="text-blue-600 hover:text-blue-800 mr-3"
                  >
                    Korish
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      handleDelete(exam.id)
                    }
                    className="text-red-600 hover:text-red-800"
                  >
                    Ochirish
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Empty state */}
        {exams.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="mb-2">
              Hali exam yaratilmagan.
            </p>

            <Link
              href="/exam/create"
              className="text-blue-600 hover:underline"
            >
              Birinchi examni yarating →
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}