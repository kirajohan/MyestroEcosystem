// app/broadcast/page.tsx
"use client";

import { useState, useEffect, useRef } from "react";
import type { BroadcastProgress, MediaType } from "@/lib/broadcasttypes";
import { useAuth } from "@/context/AuthContext";

export default function BroadcastPage() {
  const { token } = useAuth();
  const [message, setMessage] = useState("");
  const [mediaType, setMediaType] = useState<MediaType>("text");
  const [mediaUrl, setMediaUrl] = useState("");
  const [targetAll, setTargetAll] = useState(false);
  const [userIdsRaw, setUserIdsRaw] = useState("");
  const [broadcastId, setBroadcastId] = useState<string | null>(null);
  const [progress, setProgress] = useState<BroadcastProgress | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const userIds = userIdsRaw
    .split(/[,\n]/)
    .map((s) => s.trim())
    .filter(Boolean)
    .map(Number)
    .filter((n) => Number.isInteger(n));

  async function handleSend() {
    setLoading(true);
    setError(null);
    setProgress(null);
    setBroadcastId(null);
    if (pollRef.current) clearInterval(pollRef.current);

    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;
      const res = await fetch("/api/broadcast", {
        method: "POST",
        headers,
        body: JSON.stringify({
          message,
          mediaType,
          mediaUrl: mediaType === "text" ? undefined : mediaUrl,
          userIds: targetAll ? [] : userIds,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Xatolik yuz berdi");
      setBroadcastId(data.broadcastId);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

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

  return (
    <div className="mx-auto max-w-2xl p-6 space-y-6">
      <h1 className="text-2xl font-semibold text-slate-900">Broadcast yuborish</h1>

      {/* Xabar matni */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-slate-700">Xabar matni</label>
        <textarea
          className="w-full rounded-lg border border-slate-300 p-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          rows={4}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="HTML formatlash qo&apos;llab-quvvatlanadi: <b>qalin</b>, <i>qiya</i>..."
        />
      </div>

      {/* Media turi va URL */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700">Media turi</label>
          <select
            className="mt-1 w-full rounded-lg border border-slate-300 p-2 text-sm"
            value={mediaType}
            onChange={(e) => setMediaType(e.target.value as MediaType)}
          >
            <option value="text">Faqat matn</option>
            <option value="photo">Rasm</option>
            <option value="video">Video</option>
            <option value="document">Hujjat</option>
          </select>
        </div>
        {mediaType !== "text" && (
          <div>
            <label className="block text-sm font-medium text-slate-700">Media URL</label>
            <input
              className="mt-1 w-full rounded-lg border border-slate-300 p-2 text-sm"
              value={mediaUrl}
              onChange={(e) => setMediaUrl(e.target.value)}
              placeholder="https://... (public bo&apos;lishi shart)"
            />
          </div>
        )}
      </div>

      {/* Barcha foydalanuvchilarga yuborish */}
      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          id="targetAll"
          checked={targetAll}
          onChange={(e) => setTargetAll(e.target.checked)}
          className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
        />
        <label htmlFor="targetAll" className="text-sm font-medium text-slate-700">
          Barcha foydalanuvchilarga yuborish
        </label>
      </div>

      {/* Foydalanuvchi IDlari */}
      {!targetAll && (
        <div>
          <label className="block text-sm font-medium text-slate-700">
            Foydalanuvchi IDlari (vergul yoki yangi qator bilan)
          </label>
          <textarea
            className="mt-1 w-full rounded-lg border border-slate-300 p-3 text-sm font-mono"
            rows={3}
            value={userIdsRaw}
            onChange={(e) => setUserIdsRaw(e.target.value)}
            placeholder="123456789\n987654321"
          />
          <p className="mt-1 text-xs text-slate-500">{userIds.length} ta togri ID kiritildi</p>
        </div>
      )}

      {/* Xatolik */}
      {error && (
        <div className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
          {error}
        </div>
      )}

      {/* Yuborish tugmasi */}
      <button
        onClick={handleSend}
        disabled={loading || !message || (!targetAll && userIds.length === 0) || (mediaType !== "text" && !mediaUrl)}
        className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {loading ? "Yuborilmoqda..." : "Broadcast yuborish"}
      </button>

      {/* Progress bar */}
      {progress && (
        <div className="rounded-lg border border-slate-200 p-4 space-y-2">
          <div className="flex justify-between text-sm text-slate-600">
            <span>
              Holat:{" "}
              {progress.status === "pending" && "navbatda"}
              {progress.status === "sending" && "yuborilmoqda"}
              {progress.status === "completed" && "tugadi"}
            </span>
            <span>
              {progress.sent + progress.failed} / {progress.total}
            </span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
            <div
              className="h-full bg-indigo-600 transition-all"
              style={{ width: `${percent}%` }}
            />
          </div>
          <div className="flex gap-4 text-xs text-slate-500">
            <span className="text-emerald-600">Yuborildi: {progress.sent}</span>
            <span className="text-rose-600">Xato: {progress.failed}</span>
          </div>
        </div>
      )}
    </div>
  );
}
