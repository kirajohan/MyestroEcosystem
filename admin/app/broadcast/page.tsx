"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import {
  Send,
  Users,
  FileText,
  Image as ImageIcon,
  Video,
  File,
  CheckCircle2,
  XCircle,
  Clock,
  Zap,
  Loader2,
  Sparkles,
  Megaphone,
} from "lucide-react";
import confetti from "canvas-confetti";
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

// ─── Status konfiguratsiyasi ───────────────────────────────────
const STATUS_CONFIG = {
  pending: { label: "Navbatda", color: "slate", icon: Clock },
  queued: { label: "Navbatda", color: "amber", icon: Clock },
  sending: { label: "Yuborilmoqda", color: "blue", icon: Loader2 },
  completed: { label: "Tugallandi", color: "emerald", icon: CheckCircle2 },
  failed: { label: "Xato", color: "rose", icon: XCircle },
} as const;

// ─── Media turi iconlari ──────────────────────────────────────
const MEDIA_ICONS = {
  text: FileText,
  photo: ImageIcon,
  video: Video,
  document: File,
};

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
  const hasCelebrated = useRef(false);

  const handleSelectionChange = useCallback((ids: number[] | "all") => {
    setAudienceIds(ids);
  }, []);

  const handleUploadComplete = useCallback((files: UploadedFile[]) => {
    setUploadedFiles((prev) => [...prev, ...files]);
  }, []);

  const handleRemoveFile = useCallback((index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  async function handleSend() {
    if (!message.trim()) {
      setError("Xabar matni majburiy");
      return;
    }

    setLoading(true);
    setError(null);
    setProgress(null);
    setBroadcastId(null);
    hasCelebrated.current = false;
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
        console.log("📊 Broadcast status:", data);
        setProgress(data);

        // Tugagan bo'lsa — polling to'xtatish
        if (data.status === "completed" || data.status === "failed") {
          if (pollRef.current) {
            clearInterval(pollRef.current);
            pollRef.current = null;
          }
          setLoading(false);

          // Confetti faqat completed uchun
          if (data.status === "completed" && !hasCelebrated.current) {
            hasCelebrated.current = true;
            confetti({
              particleCount: 150,
              spread: 80,
              origin: { y: 0.6 },
              colors: ["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6"],
            });
          }
        }
      } catch (err) {
        console.error("❌ Polling error:", err);
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

  const statusConfig = progress
    ? STATUS_CONFIG[progress.status as keyof typeof STATUS_CONFIG] || STATUS_CONFIG.pending
    : null;

  const StatusIcon = statusConfig?.icon || Clock;

  // ─── Render ─────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
      <div className="mx-auto max-w-5xl">
        {/* ─── Header ─── */}
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-500/30">
              <Megaphone className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Broadcast</h1>
              <p className="text-sm text-slate-500">
                Foydalanuvchilarga ommaviy xabar yuborish
              </p>
            </div>
          </div>
        </div>

        {/* ─── Main Grid ─── */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* ─── Left: Form ─── */}
          <div className="space-y-6 lg:col-span-2">
            {/* Title & Message Card */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900">
                <FileText className="h-5 w-5 text-blue-500" />
                Xabar tafsilotlari
              </h2>

              <div className="space-y-4">
                {/* Title */}
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-slate-700">
                    Sarlavha
                  </label>
                  <input
                    className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Masalan: Yangi kurs haqida e'lon"
                  />
                </div>

                {/* Message */}
                <div>
                  <div className="mb-1.5 flex items-center justify-between">
                    <label className="block text-sm font-medium text-slate-700">
                      Xabar matni <span className="text-rose-500">*</span>
                    </label>
                    <PlaceholderHints />
                  </div>
                  <textarea
                    className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none resize-none"
                    rows={6}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="HTML formatlash qo'llab-quvvatlanadi: <b>qalin</b>, <i>qiya</i>...&#10;Shaxsiylashtirish: {username}, {first_name}"
                  />
                  <div className="mt-1 text-xs text-slate-400">
                    {message.length} belgi
                  </div>
                </div>
              </div>
            </div>

            {/* Media Card */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900">
                <ImageIcon className="h-5 w-5 text-purple-500" />
                Media (ixtiyoriy)
              </h2>

              <div className="grid grid-cols-4 gap-2 mb-4">
                {(Object.keys(MEDIA_ICONS) as MediaType[]).map((type) => {
                  const Icon = MEDIA_ICONS[type];
                  const labels = {
                    text: "Matn",
                    photo: "Rasm",
                    video: "Video",
                    document: "Hujjat",
                  };
                  return (
                    <button
                      key={type}
                      onClick={() => setMediaType(type)}
                      className={`flex flex-col items-center gap-1.5 rounded-xl border-2 p-3 transition-all ${
                        mediaType === type
                          ? "border-blue-500 bg-blue-50 text-blue-700"
                          : "border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50"
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                      <span className="text-xs font-medium">{labels[type]}</span>
                    </button>
                  );
                })}
              </div>

              {mediaType !== "text" && (
                <MediaUploader
                  onUploadComplete={handleUploadComplete}
                  uploadedFiles={uploadedFiles}
                  onRemove={handleRemoveFile}
                />
              )}
            </div>

            {/* Audience Card */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900">
                <Users className="h-5 w-5 text-emerald-500" />
                Qabul qiluvchilar
              </h2>

              <div className="mb-4 flex gap-2">
                <button
                  onClick={() => {
                    setTargetMode("all");
                    setAudienceIds([]);
                  }}
                  className={`flex-1 rounded-lg px-4 py-2.5 text-sm font-medium transition-all ${
                    targetMode === "all"
                      ? "bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-md shadow-blue-500/30"
                      : "border border-slate-300 text-slate-600 hover:bg-slate-50"
                  }`}
                >
                  🌍 Barcha foydalanuvchilar
                </button>
                <button
                  onClick={() => setTargetMode("manual")}
                  className={`flex-1 rounded-lg px-4 py-2.5 text-sm font-medium transition-all ${
                    targetMode === "manual"
                      ? "bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-md shadow-blue-500/30"
                      : "border border-slate-300 text-slate-600 hover:bg-slate-50"
                  }`}
                >
                  🎯 Tanlanganlarga
                </button>
              </div>

              {targetMode === "manual" && (
                <AudienceSelector onSelectionChange={handleSelectionChange} />
              )}
            </div>

            {/* Error */}
            {error && (
              <div className="flex items-start gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4">
                <XCircle className="h-5 w-5 flex-shrink-0 text-rose-500 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-rose-900">Xatolik</p>
                  <p className="text-sm text-rose-700">{error}</p>
                </div>
              </div>
            )}

            {/* Send button */}
            <button
              onClick={handleSend}
              disabled={loading || !message.trim() || !!broadcastId}
              className="group flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/30 transition-all hover:shadow-xl hover:shadow-blue-500/40 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Yuborilmoqda...
                </>
              ) : (
                <>
                  <Send className="h-5 w-5 transition-transform group-hover:translate-x-1" />
                  Broadcast yuborish
                </>
              )}
            </button>
          </div>

          {/* ─── Right: Progress / Stats ─── */}
          <div className="space-y-6">
            {!progress && !broadcastId && (
              <div className="rounded-2xl border border-dashed border-slate-300 bg-white/50 p-8 text-center">
                <Sparkles className="mx-auto h-12 w-12 text-slate-300 mb-3" />
                <p className="text-sm text-slate-500">
                  Broadcast yuborilgandan keyin bu yerda natijani korasiz
                </p>
              </div>
            )}

            {/* Status Card */}
            {progress && statusConfig && (
              <div
                className={`rounded-2xl border-2 p-6 shadow-sm transition-all ${
                  progress.status === "completed"
                    ? "border-emerald-300 bg-gradient-to-br from-emerald-50 to-green-50"
                    : progress.status === "failed"
                    ? "border-rose-300 bg-gradient-to-br from-rose-50 to-red-50"
                    : progress.status === "sending"
                    ? "border-blue-300 bg-gradient-to-br from-blue-50 to-indigo-50"
                    : "border-amber-300 bg-gradient-to-br from-amber-50 to-yellow-50"
                }`}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div
                    className={`flex h-12 w-12 items-center justify-center rounded-xl ${
                      progress.status === "completed"
                        ? "bg-emerald-500"
                        : progress.status === "failed"
                        ? "bg-rose-500"
                        : progress.status === "sending"
                        ? "bg-blue-500"
                        : "bg-amber-500"
                    }`}
                  >
                    <StatusIcon
                      className={`h-6 w-6 text-white ${
                        progress.status === "sending" ? "animate-spin" : ""
                      }`}
                    />
                  </div>
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                      Holat
                    </p>
                    <p
                      className={`text-lg font-bold ${
                        progress.status === "completed"
                          ? "text-emerald-900"
                          : progress.status === "failed"
                          ? "text-rose-900"
                          : progress.status === "sending"
                          ? "text-blue-900"
                          : "text-amber-900"
                      }`}
                    >
                      {statusConfig.label}
                    </p>
                  </div>
                </div>

                {/* Title */}
                {progress.title && (
                  <p className="mb-4 text-sm font-medium text-slate-700 line-clamp-2">
                    📢 {progress.title}
                  </p>
                )}

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="mb-1.5 flex items-center justify-between text-xs">
                    <span className="font-medium text-slate-600">
                      {progress.sent + progress.failed} / {progress.total}
                    </span>
                    <span className="font-bold text-slate-900">
                      {Math.round(percent)}%
                    </span>
                  </div>
                  <div className="h-3 w-full overflow-hidden rounded-full bg-white/70 shadow-inner">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        progress.status === "completed"
                          ? "bg-gradient-to-r from-emerald-400 to-green-500"
                          : progress.status === "failed"
                          ? "bg-gradient-to-r from-rose-400 to-red-500"
                          : "bg-gradient-to-r from-blue-400 to-indigo-500"
                      }`}
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-xl bg-white/70 p-3 text-center">
                    <CheckCircle2 className="mx-auto h-5 w-5 text-emerald-500 mb-1" />
                    <p className="text-xs text-slate-500">Yuborildi</p>
                    <p className="text-lg font-bold text-emerald-700">
                      {progress.sent}
                    </p>
                  </div>
                  <div className="rounded-xl bg-white/70 p-3 text-center">
                    <XCircle className="mx-auto h-5 w-5 text-rose-500 mb-1" />
                    <p className="text-xs text-slate-500">Xato</p>
                    <p className="text-lg font-bold text-rose-700">
                      {progress.failed}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Success Message */}
            {progress?.status === "completed" && (
              <div className="rounded-2xl border-2 border-emerald-400 bg-gradient-to-br from-emerald-500 to-green-600 p-6 text-center shadow-lg shadow-emerald-500/30">
                <div className="mb-3 flex justify-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg">
                    <CheckCircle2 className="h-10 w-10 text-emerald-500" />
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-1">
                  Muvaffaqiyatli! 🎉
                </h3>
                <p className="text-sm text-emerald-50">
                  Broadcast barcha foydalanuvchilarga yuborildi
                </p>
              </div>
            )}

            {/* Failed Message */}
            {progress?.status === "failed" && (
              <div className="rounded-2xl border-2 border-rose-400 bg-gradient-to-br from-rose-500 to-red-600 p-6 text-center shadow-lg shadow-rose-500/30">
                <div className="mb-3 flex justify-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg">
                    <XCircle className="h-10 w-10 text-rose-500" />
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-1">
                  Xatolik yuz berdi
                </h3>
                <p className="text-sm text-rose-50">
                  Iltimos qayta urinib koring
                </p>
                <button
                  onClick={() => {
                    setBroadcastId(null);
                    setProgress(null);
                    hasCelebrated.current = false;
                  }}
                  className="mt-4 rounded-lg bg-white px-4 py-2 text-sm font-medium text-rose-600 hover:bg-rose-50"
                >
                  Yangi broadcast
                </button>
              </div>
            )}

            {/* Info Card */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-start gap-3">
                <Zap className="h-5 w-5 flex-shrink-0 text-amber-500 mt-0.5" />
                <div className="text-xs text-slate-600 space-y-1">
                  <p className="font-semibold text-slate-800">Maslahatlar:</p>
                  <p>• Qisqa va aniq xabarlar yozing</p>
                  <p>• HTML formatlash qollab-quvvatlanadi</p>
                  <p>• Shaxsiylashtirish: {"{first_name}"}, {"{username}"}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}