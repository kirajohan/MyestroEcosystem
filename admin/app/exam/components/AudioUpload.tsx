"use client";

import { useState, useRef } from "react";
import { uploadMedia } from "@/lib/api";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

interface AudioUploadProps {
  currentUrl?: string | null;
  onUpload: (url: string) => void;
  onRemove?: () => void;
}

export default function AudioUpload({ currentUrl, onUpload, onRemove }: AudioUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [audioUrl, setAudioUrl] = useState(currentUrl || "");
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    // Fayl turi tekshiruvi
    if (!file.type.startsWith("audio/")) {
      setError("Faqat audio fayllar ruxsat etiladi (mp3, wav, ogg)");
      return;
    }

    // Fayl hajmi (50MB max)
    if (file.size > 50 * 1024 * 1024) {
      setError("Fayl hajmi 50MB dan oshmasligi kerak");
      return;
    }

    setUploading(true);
    setError("");

    try {
      // ✅ Server'ga yuklash
      const result = await uploadMedia(file, "audio");
      setAudioUrl(result.url);
      onUpload(result.url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Yuklashda xato");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  function handleRemove() {
    setAudioUrl("");
    onUpload("");
    onRemove?.();
  }

  return (
    <div className="space-y-3">
      {/* Hozirgi audio (agar bor bo'lsa) */}
      {audioUrl && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-emerald-700">
              🎧 Audio fayl yuklangan
            </span>
            <button
              onClick={handleRemove}
              className="text-red-600 hover:text-red-800 text-sm font-semibold"
            >
              ✕ Olib tashlash
            </button>
          </div>

          {/* Audio Player */}
          <audio controls className="w-full" style={{ height: "40px" }}>
            <source src={`${API_BASE_URL}${audioUrl}`} type="audio/mpeg" />
            Brauzeringiz audio elementni qollab-quvvatlamaydi.
          </audio>

          <p className="text-xs text-slate-500 mt-2 font-mono truncate">
            {audioUrl}
          </p>
        </div>
      )}

      {/* Upload tugmasi */}
      <div>
        <label className="block text-sm font-medium mb-1.5 text-slate-700">
          Audio fayl {audioUrl ? "(o'zgartirish)" : "yuklash"}
        </label>

        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          onChange={handleFileChange}
          disabled={uploading}
          className="block w-full text-sm text-slate-600
            file:mr-4 file:py-2 file:px-4
            file:rounded-lg file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100
            file:cursor-pointer
            disabled:opacity-50 disabled:cursor-not-allowed"
        />

        {uploading && (
          <div className="mt-2 flex items-center gap-2 text-sm text-blue-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            Yuklanmoqda...
          </div>
        )}

        {error && (
          <div className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded">
            ❌ {error}
          </div>
        )}
      </div>
    </div>
  );
}