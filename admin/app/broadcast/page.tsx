'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
  AlertCircle,
  RotateCcw,
} from 'lucide-react';
import confetti from 'canvas-confetti';
import type { BroadcastProgress, MediaType } from '@/lib/broadcasttypes';
import AudienceSelector from '@/components/broadcast/AudienceSelector';
import MediaUploader from '@/components/broadcast/MediaUploader';
import PlaceholderHints from '@/components/broadcast/PlaceholderHints';

interface UploadedFile {
  filename: string;
  content_type: string;
  file_id: string;
  telegram_file_id?: string;
}

const STATUS_CONFIG = {
  pending: { label: 'Navbatda', color: 'slate', icon: Clock },
  queued: { label: 'Navbatda', color: 'amber', icon: Clock },
  sending: { label: 'Yuborilmoqda', color: 'orange', icon: Loader2 },
  completed: { label: 'Tugallandi', color: 'emerald', icon: CheckCircle2 },
  failed: { label: 'Xato', color: 'red', icon: XCircle },
} as const;

const MEDIA_ICONS = {
  text: FileText,
  photo: ImageIcon,
  video: Video,
  document: File,
};

const MEDIA_LABELS: Record<string, string> = {
  text: 'Matn',
  photo: 'Rasm',
  video: 'Video',
  document: 'Hujjat',
};

export default function BroadcastPage() {
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [mediaType, setMediaType] = useState<MediaType>('text');
  const [targetMode, setTargetMode] = useState<'all' | 'manual'>('all');
  const [audienceIds, setAudienceIds] = useState<number[] | 'all'>([]);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [broadcastId, setBroadcastId] = useState<string | null>(null);
  const [progress, setProgress] = useState<BroadcastProgress | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const hasCelebrated = useRef(false);
  const messageTextareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSelectionChange = useCallback((ids: number[] | 'all') => {
    setAudienceIds(ids);
  }, []);

  const handleUploadComplete = useCallback((files: UploadedFile[]) => {
    setUploadedFiles((prev) => [...prev, ...files]);
  }, []);

  const handleRemoveFile = useCallback((index: number) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleInsertPlaceholder = (placeholder: string) => {
    const textarea = messageTextareaRef.current;
    if (!textarea) {
      setMessage((prev) => prev + placeholder);
      return;
    }

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const before = message.substring(0, start);
    const after = message.substring(end);
    const newMessage = before + placeholder + after;

    setMessage(newMessage);

    setTimeout(() => {
      textarea.focus();
      const newPos = start + placeholder.length;
      textarea.setSelectionRange(newPos, newPos);
    }, 10);
  };

  async function handleSend() {
    if (!message.trim()) {
      setError('Xabar matni majburiy');
      return;
    }

    setLoading(true);
    setError(null);
    setProgress(null);
    setBroadcastId(null);
    hasCelebrated.current = false;
    if (pollRef.current) clearInterval(pollRef.current);

    try {
      const fileId =
        uploadedFiles.length > 0
          ? uploadedFiles[0].telegram_file_id || uploadedFiles[0].file_id
          : null;

      let targetModePayload = 'all';
      let targetUserIds: number[] | undefined;

      if (Array.isArray(audienceIds) && audienceIds.length > 0) {
        targetModePayload = 'manual';
        targetUserIds = audienceIds;
      }

      const payload: any = {
        title: title || `Broadcast - ${new Date().toLocaleString('uz-UZ')}`,
        content: message,
        message_type: mediaType,
        file_id: fileId,
        target_mode: targetModePayload,
      };

      if (targetModePayload === 'manual' && targetUserIds) {
        payload.target_user_ids = targetUserIds;
      }

      const res = await fetch('/api/broadcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? 'Xatolik yuz berdi');
      setBroadcastId(data.broadcastId || data.broadcast_id);
    } catch (e) {
      setError((e as Error).message);
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!broadcastId) return;

    async function poll() {
      try {
        const res = await fetch(`/api/broadcast/status/${broadcastId}`);
        if (!res.ok) return;
        const data: BroadcastProgress = await res.json();
        setProgress(data);

        if (data.status === 'completed' || data.status === 'failed') {
          if (pollRef.current) {
            clearInterval(pollRef.current);
            pollRef.current = null;
          }
          setLoading(false);

          if (data.status === 'completed' && !hasCelebrated.current) {
            hasCelebrated.current = true;
            confetti({
              particleCount: 150,
              spread: 80,
              origin: { y: 0.6 },
              colors: ['#f97316', '#fb923c', '#fbbf24', '#10b981'],
            });
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-orange-50/30 p-4 md:p-6">
      <div className="mx-auto max-w-6xl">
        {/* ─── Header ─── */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 shadow-lg shadow-orange-500/30">
              <Megaphone className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Broadcast</h1>
              <p className="text-sm text-slate-500">
                Foydalanuvchilarga shaxsiylashtirilgan ommaviy xabar yuborish
              </p>
            </div>
          </div>
        </div>

        {/* ─── Main Grid ─── */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* ─── Left: Form ─── */}
          <div className="space-y-5 lg:col-span-2">
            {/* Title & Message Card */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden"
            >
              <div className="p-5 border-b border-slate-100 bg-gradient-to-r from-orange-500 to-orange-600">
                <h2 className="flex items-center gap-2 text-base font-bold text-white">
                  <FileText className="h-5 w-5" />
                  Xabar tafsilotlari
                </h2>
                <p className="text-xs text-white/80 mt-0.5">
                  Sarlavha va shaxsiylashtirilgan xabar matnini kiriting
                </p>
              </div>

              <div className="p-5 space-y-4">
                {/* Title */}
                <div>
                  <label className="mb-1.5 block text-sm font-semibold text-slate-900">
                    Sarlavha
                  </label>
                  <input
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Masalan: Yangi kurs haqida elon"
                  />
                </div>

                {/* Message */}
                <div>
                  <div className="mb-2">
                    <label className="block text-sm font-semibold text-slate-900 mb-1">
                      Xabar matni <span className="text-red-500">*</span>
                    </label>
                    <p className="text-xs text-slate-500">
                      Placeholder har bir foydalanuvchi uchun avtomatik toldiriladi
                    </p>
                  </div>

                  <textarea
                    ref={messageTextareaRef}
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all resize-none font-mono"
                    rows={8}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Salom {first_name}! Sizga yangi yangiliklar..."
                  />

                  <div className="mt-2 flex items-center justify-between">
                    <span className="text-xs text-slate-500">
                      <span className="font-medium text-slate-700">{message.length}</span> belgi
                    </span>
                  </div>

                  {/* Placeholder Hints */}
                  <div className="mt-3">
                    <PlaceholderHints onInsert={handleInsertPlaceholder} />
                  </div>
                </div>

                {/* Preview */}
                {message.trim() && (
                  <div className="rounded-xl border border-orange-200 bg-orange-50/50 p-4">
                    <p className="text-xs font-semibold text-orange-700 mb-2 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" />
                      Oldindan korinish
                    </p>
                    <div
                      className="text-sm text-slate-800 whitespace-pre-wrap break-words"
                      dangerouslySetInnerHTML={{ __html: message.replace(/\n/g, '<br/>') }}
                    />
                  </div>
                )}
              </div>
            </motion.div>

            {/* Media Card */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <h2 className="mb-4 flex items-center gap-2 text-base font-bold text-slate-900">
                <ImageIcon className="h-5 w-5 text-orange-500" />
                Media (ixtiyoriy)
              </h2>

              <div className="grid grid-cols-4 gap-2 mb-4">
                {(Object.keys(MEDIA_ICONS) as MediaType[]).map((type) => {
                  const Icon = MEDIA_ICONS[type];
                  const isSelected = mediaType === type;
                  return (
                    <button
                      key={type}
                      onClick={() => setMediaType(type)}
                      className={`flex flex-col items-center gap-1.5 rounded-xl border-2 p-3 transition-all ${
                        isSelected
                          ? 'border-orange-500 bg-orange-50 text-orange-700 shadow-sm'
                          : 'border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50'
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                      <span className="text-xs font-medium">{MEDIA_LABELS[type]}</span>
                    </button>
                  );
                })}
              </div>

              {mediaType !== 'text' && (
                <MediaUploader
                  onUploadComplete={handleUploadComplete}
                  uploadedFiles={uploadedFiles}
                  onRemove={handleRemoveFile}
                />
              )}
            </motion.div>

            {/* Audience Card */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <h2 className="mb-4 flex items-center gap-2 text-base font-bold text-slate-900">
                <Users className="h-5 w-5 text-orange-500" />
                Qabul qiluvchilar
              </h2>

              <div className="mb-4 grid grid-cols-2 gap-2">
                <button
                  onClick={() => {
                    setTargetMode('all');
                    setAudienceIds([]);
                  }}
                  className={`rounded-xl px-4 py-3 text-sm font-medium transition-all ${
                    targetMode === 'all'
                      ? 'bg-gradient-to-r from-orange-500 to-orange-600 text-white shadow-md shadow-orange-500/20'
                      : 'border border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <div className="text-lg mb-0.5">🌍</div>
                  <div>Barcha foydalanuvchilar</div>
                </button>
                <button
                  onClick={() => setTargetMode('manual')}
                  className={`rounded-xl px-4 py-3 text-sm font-medium transition-all ${
                    targetMode === 'manual'
                      ? 'bg-gradient-to-r from-orange-500 to-orange-600 text-white shadow-md shadow-orange-500/20'
                      : 'border border-slate-200 text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <div className="text-lg mb-0.5">🎯</div>
                  <div>Tanlanganlarga</div>
                </button>
              </div>

              <AnimatePresence>
                {targetMode === 'manual' && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                  >
                    <AudienceSelector onSelectionChange={handleSelectionChange} />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Error */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4"
                >
                  <AlertCircle className="h-5 w-5 flex-shrink-0 text-red-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-red-900">Xatolik</p>
                    <p className="text-sm text-red-700 mt-0.5">{error}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Send button */}
            <button
              onClick={handleSend}
              disabled={loading || !message.trim() || !!broadcastId}
              className="group flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-orange-500 to-orange-600 px-6 py-4 text-sm font-semibold text-white shadow-lg shadow-orange-500/30 transition-all hover:shadow-xl hover:shadow-orange-500/40 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
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
          <div className="space-y-5">
            {!progress && !broadcastId && (
              <div className="rounded-2xl border-2 border-dashed border-slate-200 bg-white/50 p-8 text-center">
                <Sparkles className="mx-auto h-12 w-12 text-orange-300 mb-3" />
                <p className="text-sm text-slate-600 font-medium">
                  Broadcast yuborilgandan keyin
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  bu yerda natijani korasiz
                </p>
              </div>
            )}

            {/* Status Card */}
            <AnimatePresence>
              {progress && statusConfig && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className={`rounded-2xl border-2 p-5 shadow-sm ${
                    progress.status === 'completed'
                      ? 'border-emerald-300 bg-gradient-to-br from-emerald-50 to-green-50'
                      : progress.status === 'failed'
                      ? 'border-red-300 bg-gradient-to-br from-red-50 to-rose-50'
                      : progress.status === 'sending'
                      ? 'border-orange-300 bg-gradient-to-br from-orange-50 to-amber-50'
                      : 'border-amber-300 bg-gradient-to-br from-amber-50 to-yellow-50'
                  }`}
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div
                      className={`flex h-12 w-12 items-center justify-center rounded-xl shadow-sm ${
                        progress.status === 'completed'
                          ? 'bg-emerald-500'
                          : progress.status === 'failed'
                          ? 'bg-red-500'
                          : progress.status === 'sending'
                          ? 'bg-orange-500'
                          : 'bg-amber-500'
                      }`}
                    >
                      <StatusIcon
                        className={`h-6 w-6 text-white ${
                          progress.status === 'sending' ? 'animate-spin' : ''
                        }`}
                      />
                    </div>
                    <div>
                      <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                        Holat
                      </p>
                      <p
                        className={`text-lg font-bold ${
                          progress.status === 'completed'
                            ? 'text-emerald-900'
                            : progress.status === 'failed'
                            ? 'text-red-900'
                            : progress.status === 'sending'
                            ? 'text-orange-900'
                            : 'text-amber-900'
                        }`}
                      >
                        {statusConfig.label}
                      </p>
                    </div>
                  </div>

                  {progress.title && (
                    <p className="mb-4 text-sm font-medium text-slate-700 line-clamp-2 bg-white/60 rounded-lg p-2">
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
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${percent}%` }}
                        transition={{ duration: 0.5 }}
                        className={`h-full rounded-full ${
                          progress.status === 'completed'
                            ? 'bg-gradient-to-r from-emerald-400 to-green-500'
                            : progress.status === 'failed'
                            ? 'bg-gradient-to-r from-red-400 to-rose-500'
                            : 'bg-gradient-to-r from-orange-400 to-orange-500'
                        }`}
                      />
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-2">
                    <div className="rounded-xl bg-white/70 p-3 text-center">
                      <CheckCircle2 className="mx-auto h-5 w-5 text-emerald-500 mb-1" />
                      <p className="text-xs text-slate-500">Yuborildi</p>
                      <p className="text-lg font-bold text-emerald-700">{progress.sent}</p>
                    </div>
                    <div className="rounded-xl bg-white/70 p-3 text-center">
                      <XCircle className="mx-auto h-5 w-5 text-red-500 mb-1" />
                      <p className="text-xs text-slate-500">Xato</p>
                      <p className="text-lg font-bold text-red-700">{progress.failed}</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Success Message */}
            <AnimatePresence>
              {progress?.status === 'completed' && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="rounded-2xl border-2 border-emerald-400 bg-gradient-to-br from-emerald-500 to-green-600 p-6 text-center shadow-lg shadow-emerald-500/30"
                >
                  <div className="mb-3 flex justify-center">
                    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg">
                      <CheckCircle2 className="h-10 w-10 text-emerald-500" />
                    </div>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-1">Muvaffaqiyatli! 🎉</h3>
                  <p className="text-sm text-emerald-50">
                    Broadcast barcha foydalanuvchilarga yuborildi
                  </p>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Failed Message */}
            <AnimatePresence>
              {progress?.status === 'failed' && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="rounded-2xl border-2 border-red-400 bg-gradient-to-br from-red-500 to-rose-600 p-6 text-center shadow-lg shadow-red-500/30"
                >
                  <div className="mb-3 flex justify-center">
                    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white shadow-lg">
                      <XCircle className="h-10 w-10 text-red-500" />
                    </div>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-1">Xatolik yuz berdi</h3>
                  <p className="text-sm text-red-50">Iltimos qayta urinib koring</p>
                  <button
                    onClick={() => {
                      setBroadcastId(null);
                      setProgress(null);
                      hasCelebrated.current = false;
                    }}
                    className="mt-4 inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 transition"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Yangi broadcast
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

              {/* Placeholder Card */}
              <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-4">
                  <div className="flex items-center gap-2">
                    <div className="w-9 h-9 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                      <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-white">Placeholderlar</h3>
                      <p className="text-xs text-white/80">
                        Bosib nusxalang va xabarga qoying
                      </p>
                    </div>
                  </div>
                </div>
                <div className="p-4">
                  <PlaceholderHints />
                </div>
              </div>
          </div>
        </div>
      </div>
    </div>
  );
}