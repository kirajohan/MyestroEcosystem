// app/broadcast/page.tsx
"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import type { BroadcastProgress, MediaType } from "@/lib/broadcasttypes";
import type { FilterState } from "@/hooks/useAudienceSelection";
import AudienceSelector from "@/components/broadcast/AudienceSelector";
import MediaUploader from "@/components/broadcast/MediaUploader";
import PlaceholderHints from "@/components/broadcast/PlaceholderHints";

interface UploadedFile {
  filename: string;
  content_type: string;
  file_id: string;
  telegram_file_id?: string;
}

interface HistoryItem {
  broadcast_id: string;
  title: string;
  status: string;
  total: number;
  sent: number;
  failed: number;
  created_at: string;
}



const sendBroadcast = async (payload: any) => {
  const token = localStorage.getItem('access_token'); // ⬅️ Browser'dan olamiz
  
  const response = await fetch('/api/broadcast', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`, // ⬅️ Headerga qo'shamiz
    },
    body: JSON.stringify(payload),
  });
  
  return response.json();
};

export default function BroadcastPage() {
  // Form state
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [mediaType, setMediaType] = useState<MediaType>("text");
  const [targetMode, setTargetMode] = useState<"all" | "manual" | "filter">("all");
  const [audienceIds, setAudienceIds] = useState<number[] | "all">([]);
  const [audienceFilter, setAudienceFilter] = useState<FilterState | undefined>();
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [broadcastId, setBroadcastId] = useState<string | null>(null);
  const [progress, setProgress] = useState<BroadcastProgress | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // History state
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  // Fetch history
  useEffect(() => {
    async function fetchHistory() {
      try {
        const res = await fetch("/api/broadcast/history");
        if (res.ok) {
          const data = await res.json();
          setHistory(Array.isArray(data) ? data : []);
        }
      } catch (e) {
        console.error("Failed to fetch history:", e);
      } finally {
        setHistoryLoading(false);
      }
    }
    fetchHistory();
  }, [broadcastId]);

  // Handle audience selection
  const handleSelectionChange = useCallback((ids: number[] | "all", filter?: FilterState) => {
    setAudienceIds(ids);
    setAudienceFilter(filter);
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
      // Determine file_id from uploaded files
      const fileId = uploadedFiles.length > 0
        ? (uploadedFiles[0].telegram_file_id || uploadedFiles[0].file_id)
        : null;

      // Build target payload
      let targetModePayload = "all";
      let targetUserIds: number[] | undefined;
      let targetFilter: FilterState | undefined;

      if (audienceIds === "all" && targetMode === "filter") {
        targetModePayload = "filter";
        targetFilter = audienceFilter;
      } else if (Array.isArray(audienceIds) && audienceIds.length > 0) {
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
      if (targetModePayload === "filter" && targetFilter) {
        payload.target_filter = targetFilter;
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
        const res = await fetch(`/api/broadcast/${broadcastId}`);
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

  const historyRefreshKey = broadcastId;

  return (
    <div className="mx-auto max-w-6xl p-6">
      <h1 className="mb-6 text-2xl font-semibold text-gray-900">Broadcast yuborish</h1>

      <div className="flex gap-6">
        {/* Left panel — Broadcast form */}
        <div className="flex-1 space-y-5">
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

          {/* Media type + upload */}
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
                onClick={() => setTargetMode("filter")}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium ${
                  targetMode === "filter"
                    ? "bg-primary text-white"
                    : "border border-gray-300 text-gray-600 hover:bg-dark-100"
                }`}
              >
                Filtr bo&#39;yicha
              </button>
            </div>
          </div>

          {/* Audience selector (only for filter/manual mode) */}
          {targetMode === "filter" && (
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

        {/* Right panel — Broadcast History */}
        <div className="w-80 shrink-0">
          <div className="rounded-lg border border-gray-200 bg-white">
            <div className="border-b border-gray-200 px-4 py-3">
              <h2 className="text-sm font-semibold text-gray-800">Broadcast tarixi</h2>
            </div>
            <div className="max-h-[70vh] overflow-y-auto p-3">
              {historyLoading ? (
                <div className="py-8 text-center text-sm text-gray-400">Yuklanmoqda...</div>
              ) : history.length === 0 ? (
                <div className="py-8 text-center text-sm text-gray-400">Hali broadcast yuborilmagan</div>
              ) : (
                <div className="space-y-2">
                  {history.map((item) => (
                    <div
                      key={item.broadcast_id}
                      className="rounded-lg border border-gray-100 bg-primary-50/50 p-3 text-xs"
                    >
                      <div className="mb-1 font-medium text-gray-800 truncate">
                        {item.title || "Sarlavhasiz"}
                      </div>
                      <div className="mb-1.5 flex items-center gap-2 text-gray-500">
                        <span>{new Date(item.created_at).toLocaleDateString("uz-UZ")}</span>
                        <span
                          className={`inline-block rounded-full px-1.5 py-0.5 text-[10px] font-medium ${
                            item.status === "completed"
                              ? "bg-emerald-100 text-emerald-700"
                              : item.status === "sending"
                              ? "bg-amber-100 text-amber-700"
                              : item.status === "failed"
                              ? "bg-rose-100 text-rose-700"
                              : "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {item.status === "completed" && "Tugadi"}
                          {item.status === "sending" && "Yuborilmoqda"}
                          {item.status === "queued" && "Navbatda"}
                          {item.status === "pending" && "Kutilmoqda"}
                          {item.status === "failed" && "Xato"}
                          {!["completed", "sending", "queued", "pending", "failed"].includes(item.status) && item.status}
                        </span>
                      </div>
                      <div className="flex gap-3 text-gray-400">
                        <span className="text-emerald-600">✓ {item.sent}</span>
                        <span className="text-rose-600">✗ {item.failed}</span>
                        <span>Jami: {item.total}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}