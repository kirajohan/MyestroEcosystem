"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import type { BroadcastProgress, MediaType } from "@/lib/broadcasttypes";
import AudienceSelector from "@/components/broadcast/AudienceSelector";
import MediaUploader from "@/components/broadcast/MediaUploader";
import PlaceholderHints from "@/components/broadcast/PlaceholderHints";

interface UploadedFile {
  filename: string;
  content_type: string;
  file_id: string;
  telegram_file_id?: string;
}

export default function BroadcastPage() {
  // Form state
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [mediaType, setMediaType] = useState<MediaType>("text");
  const [targetMode, setTargetMode] = useState<"all" | "manual">("all");
  const [audienceIds, setAudienceIds] = useState<number[] | "all">([]);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [broadcastId, setBroadcastId] = useState<string | null>(null);
  const [progress, setProgress] = useState<BroadcastProgress | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Handle audience selection
  const handleSelectionChange = useCallback((ids: number[] | "all") => {
    setAudienceIds(ids);
  }, []);

  // Handle media upload
  const handleUploadComplete = useCallback((files: UploadedFile[]) => {
    setUploadedFiles((prev) => [...prev, ...files]);
  }, []);

  const handleRemoveFile = useCallback((index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  async function handleSend() {
    setLoading(true);
    setError(null);
    setProgress(null);
    setBroadcastId(null);
    if (pollRef.current) clearInterval(pollRef.current);

    try {
      const fileId = uploadedFiles.length > 0
        ? (uploadedFiles[0].telegram_file_id || uploadedFiles[0].file_id)
        : null;

      let targetModePayload = "all";
      let targetUserIds: number[] | undefined;

      if (Array.isArray(audienceIds) && audienceIds.length > 0) {
        targetModePayload = "manual";
        targetUserIds = audienceIds;
      }

      const payload: any = {
        title: title || `Broadcast - ${new Date().toLocaleString("uz-UZ")}`,
        content: message,
        message_type: mediaType,
        file_id: fileId,
        target_mode: targetModePayload,
      };

      if (targetModePayload === "manual" && targetUserIds) {
        payload.target_user_ids = targetUserIds;
      }

      const res = await fetch("/api/broadcast", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Xatolik yuz berdi");
      setBroadcastId(data.broadcastId || data.broadcast_id);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  // Poll progress
  useEffect(() => {
    if (!broadcastId) return;

    async function poll() {
      try {
        const res = await fetch(`/api/broadcast/status/${broadcastId}`);
        if (!res.ok) return;
        const data: BroadcastProgress = await res.json();
        setProgress(data);
        if ((data.status === "completed" || data.status === "failed") && pollRef.current) {
          clearInterval(pollRef.current);
        }
      } catch {
        // Vaqtinchalik tarmoq xatosi
      }
    }

    poll();
    pollRef.current = setInterval(poll, 2000);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [broadcastId]);

  const percent = progress
    ? Math.min(100, ((progress.sent + progress.failed) / (progress.total || 1)) * 100)
    : 0;

  return (
    <div className="mx-auto max-w-4xl p-6">
      <h1 className="mb-6 text-2xl font-semibold text-gray-900">Broadcast yuborish</h1>

      <div className="space-y-5">
        {/* Title */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Sarlavha</label>
          <input
            className="w-full rounded-lg border border-gray-300 p-2.5 text-sm focus:border-primary focus:ring-1 focus:ring-primary"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Broadcast sarlavhasi..."
          />
        </div>

        {/* Message with placeholder hints */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Xabar matni</label>
          <PlaceholderHints />
          <textarea
            className="w-full rounded-lg border border-gray-300 p-3 text-sm focus:border-primary focus:ring-1 focus:ring-primary"
            rows={5}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="HTML formatlash qo'llab-quvvatlanadi: <b>qalin</b>, <i>qiya</i>... Shaxsiylashtirish uchun {username}, {first_name} va boshqa kalit so'zlardan foydalaning."
          />
        </div>

        {/* Media type */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Media turi</label>
            <select
              className="mt-1 w-full rounded-lg border border-gray-300 p-2 text-sm"
              value={mediaType}
              onChange={(e) => setMediaType(e.target.value as MediaType)}
            >
              <option value="text">Faqat matn</option>
              <option value="photo">Rasm</option>
              <option value="video">Video</option>
              <option value="document">Hujjat</option>
            </select>
          </div>
        </div>

        {/* Media uploader */}
        {mediaType !== "text" && (
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Media fayl (Telegram orqali yuklash)
            </label>
            <MediaUploader
              onUploadComplete={handleUploadComplete}
              uploadedFiles={uploadedFiles}
              onRemove={handleRemoveFile}
            />
          </div>
        )}

        {/* Target audience mode selector */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Qabul qiluvchilar</label>
          <div className="flex gap-2">
            <button
              onClick={() => { setTargetMode("all"); setAudienceIds([]); }}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium ${
                targetMode === "all"
                  ? "bg-primary text-white"
                  : "border border-gray-300 text-gray-600 hover:bg-dark-100"
              }`}
            >
              Barcha foydalanuvchilar
            </button>
            <button
              onClick={() => setTargetMode("manual")}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium ${
                targetMode === "manual"
                  ? "bg-primary text-white"
                  : "border border-gray-300 text-gray-600 hover:bg-dark-100"
              }`}
            >
              Tanlanganlarga
            </button>
          </div>
        </div>

        {/* Audience selector (only for manual mode) */}
        {targetMode === "manual" && (
          <AudienceSelector onSelectionChange={handleSelectionChange} />
        )}

        {/* Error */}
        {error && (
          <div className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
            {error}
          </div>
        )}

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={loading || !message}
          className="rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
        >
          {loading ? "Yuborilmoqda..." : "Broadcast yuborish"}
        </button>

        {/* Progress bar */}
        {progress && (
          <div className="rounded-lg border border-gray-200 p-4 space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>
                Holat:{" "}
                {progress.status === "pending" && "navbatda"}
                {progress.status === "queued" && "navbatda"}
                {progress.status === "sending" && "yuborilmoqda"}
                {progress.status === "completed" && "tugadi"}
                {progress.status === "failed" && "xato"}
              </span>
              <span>
                {progress.sent + progress.failed} / {progress.total}
              </span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${percent}%` }}
              />
            </div>
            <div className="flex gap-4 text-xs text-gray-500">
              <span className="text-emerald-600">Yuborildi: {progress.sent}</span>
              <span className="text-rose-600">Xato: {progress.failed}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}