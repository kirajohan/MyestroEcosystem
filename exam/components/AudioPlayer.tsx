"use client";

import { API_URL } from "@/lib/api";

interface AudioPlayerProps {
  audioUrl: string;
}

export default function AudioPlayer({ audioUrl }: AudioPlayerProps) {
  const fullUrl = `${API_URL}${audioUrl}`;

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6">
      <audio
        controls
        className="w-full"
        style={{ height: "48px" }}
        preload="metadata"
      >
        <source src={fullUrl} type="audio/mpeg" />
        Brauzeringiz audio elementni qo'llab-quvvatlamaydi.
      </audio>

      <div className="mt-3 space-y-1.5 text-sm text-slate-600">
        <div className="flex items-center gap-2">
          <span className="text-blue-600">🎧</span>
          <span>Audioni diqqat bilan tinglang</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-blue-600">💡</span>
          <span>Kerak bo'lsa, bir necha marta tinglashingiz mumkin</span>
        </div>
      </div>
    </div>
  );
}