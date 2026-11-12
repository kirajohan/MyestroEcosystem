"use client";

import { useState, useRef, useEffect } from "react";
import { motion  } from "framer-motion";
import { getSessionToken } from "@/lib/session";
import { useLanguage } from "@/app/providers";

interface SpeakingRecorderProps {
  itemId: number;
  attemptId: number;
  topic: string;
  instruction?: string;
  preparationTimeSec?: number;
  answerTimeSec?: number;
  apiUrl: string;
  onUploaded?: () => void;
}

type Stage = "idle" | "preparing" | "ready" | "recording" | "review" | "uploading" | "done";

export default function SpeakingRecorder({
  itemId,
  attemptId,
  topic,
  instruction,
  preparationTimeSec = 30,
  answerTimeSec = 60,
  apiUrl,
  onUploaded,
}: SpeakingRecorderProps) {
  const { t } = useLanguage();
  const [stage, setStage] = useState<Stage>("idle");
  const [prepLeft, setPrepLeft] = useState(preparationTimeSec);
  const [recordLeft, setRecordLeft] = useState(answerTimeSec);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [micError, setMicError] = useState("");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [waveform, setWaveform] = useState<number[]>(Array(24).fill(4));

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const rafRef = useRef<number | null>(null);

  // Cleanup
  useEffect(() => {
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
      }
      if (audioCtxRef.current) audioCtxRef.current.close();
    };
  }, []);

  // ── Mikrofonni ochish ──────────────────────────────────
  const getMicrophone = async (): Promise<MediaStream | null> => {
    try {
      setMicError("");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      return stream;
    } catch (err) {
      setMicError(t("speak.mic_denied"));
      return null;
    }
  };

  // ── Waveform visualization ─────────────────────────────
  const startWaveform = (stream: MediaStream) => {
    const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
    const ctx = new AudioCtx();
    audioCtxRef.current = ctx;
    const source = ctx.createMediaStreamSource(stream);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 64;
    source.connect(analyser);
    analyserRef.current = analyser;

    const data = new Uint8Array(analyser.frequencyBinCount);
    const tick = () => {
      analyser.getByteFrequencyData(data);
      const bars = Array.from({ length: 24 }, (_, i) => {
        const v = data[i % data.length] || 0;
        return Math.max(4, Math.min(40, (v / 255) * 40));
      });
      setWaveform(bars);
      rafRef.current = requestAnimationFrame(tick);
    };
    tick();
  };

  const stopWaveform = () => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    setWaveform(Array(24).fill(4));
  };

  // ── Preparation timer ──────────────────────────────────
  const startPreparation = async () => {
    const stream = await getMicrophone();
    if (!stream) return;

    setStage("preparing");
    setPrepLeft(preparationTimeSec);

    const interval = setInterval(() => {
      setPrepLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          setStage("ready");
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  // ── Recording ──────────────────────────────────────────
  const startRecording = async () => {
    let stream = streamRef.current;
    if (!stream) {
      stream = await getMicrophone();
      if (!stream) return;
    }

    chunksRef.current = [];
    const mimeType = MediaRecorder.isTypeSupported("audio/webm")
      ? "audio/webm"
      : "audio/mp4";

    const recorder = new MediaRecorder(stream, {
      mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm',
      audioBitsPerSecond: 32000, 
    });    mediaRecorderRef.current = recorder;

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: mimeType });
      setAudioBlob(blob);
      setAudioUrl(URL.createObjectURL(blob));
      setStage("review");
      stopWaveform();
    };

    recorder.start();
    startWaveform(stream);
    setStage("recording");
    setRecordLeft(answerTimeSec);

    const interval = setInterval(() => {
      setRecordLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          if (mediaRecorderRef.current?.state === "recording") {
            mediaRecorderRef.current.stop();
          }
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
  };

  const recordAgain = () => {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    setAudioUrl(null);
    setAudioBlob(null);
    startRecording();
  };

  // ── Upload ─────────────────────────────────────────────
  const submitAudio = async () => {
    if (!audioBlob) return;

    setStage("uploading");
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append("file", audioBlob, `speaking_${itemId}.webm`);

      const xhr = new XMLHttpRequest();
      xhr.open(
        "POST",
        `${apiUrl}/api/v2/exam/attempts/${attemptId}/answers/${itemId}/audio`
      );
      // Backend sessiyani cookie emas, Bearer token orqali tekshiradi (apiFetch kabi)
      const token = getSessionToken();
      if (token) xhr.setRequestHeader("Authorization", `Bearer ${token}`);

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          setUploadProgress(Math.round((e.loaded / e.total) * 100));
        }
      };

      await new Promise<void>((resolve, reject) => {
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) resolve();
          else reject(new Error(`HTTP ${xhr.status}`));
        };
        xhr.onerror = () => reject(new Error(t("speak.upload_error")));
        xhr.send(formData);
      });

      setStage("done");
      onUploaded?.();
    } catch (err) {
      setMicError(err instanceof Error ? err.message : t("speak.upload_error"));
      setStage("review");
    }
  };

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
  };

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-rose-50 to-orange-50 dark:from-slate-900 dark:to-slate-900 border border-rose-200/60 dark:border-rose-900/50 shadow-xl p-6 md:p-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <motion.div
          animate={{ rotate: [0, 8, -8, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-500 to-orange-500 flex items-center justify-center text-2xl shadow-lg"
        >
          🎤
        </motion.div>
        <div>
          <div className="text-xs uppercase tracking-widest text-rose-600 font-bold">
            {t("speak.task")}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400">
            {t("speak.timing", { a: preparationTimeSec, b: answerTimeSec })}
          </div>
        </div>
      </div>

      {/* Topic */}
      <div className="bg-white/70 dark:bg-slate-800/70 rounded-xl p-4 mb-5 border border-rose-100 dark:border-slate-700">
        {instruction && (
          <p className="text-sm text-slate-600 dark:text-slate-300 mb-2">{instruction}</p>
        )}
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">{topic}</h3>
      </div>

      {/* Error */}
      {micError && (
        <div className="bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 p-3 rounded-xl text-sm mb-4">
          ⚠️ {micError}
        </div>
      )}

      {/* ═══ STAGE: IDLE ═══ */}
      {stage === "idle" && (
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={startPreparation}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-rose-500 to-orange-500 text-white font-bold text-lg shadow-lg hover:shadow-xl transition-shadow"
        >
          {t("speak.start")}
        </motion.button>
      )}

      {/* ═══ STAGE: PREPARING ═══ */}
      {stage === "preparing" && (
        <div className="text-center py-6">
          <div className="text-sm text-slate-600 dark:text-slate-300 mb-3">
            {t("speak.think")}
          </div>
          <motion.div
            key={prepLeft}
            initial={{ scale: 1.2 }}
            animate={{ scale: 1 }}
            className="text-5xl font-bold text-rose-600 mb-4 tabular-nums"
          >
            {prepLeft}
          </motion.div>
          <div className="h-2 bg-rose-100 rounded-full overflow-hidden mb-4">
            <motion.div
              className="h-full bg-gradient-to-r from-rose-500 to-orange-500"
              animate={{
                width: `${(prepLeft / preparationTimeSec) * 100}%`,
              }}
              transition={{ duration: 1, ease: "linear" }}
            />
          </div>
          <button
            onClick={() => setStage("ready")}
            className="text-sm text-rose-600 hover:text-rose-700 font-semibold"
          >
            {t("speak.skip_prep")}
          </button>
        </div>
      )}

      {/* ═══ STAGE: READY ═══ */}
      {stage === "ready" && (
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={startRecording}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-red-500 to-rose-600 text-white font-bold text-lg shadow-lg hover:shadow-xl transition-shadow flex items-center justify-center gap-3"
        >
          <span className="w-3 h-3 rounded-full bg-white dark:bg-slate-900 animate-pulse" />
          {t("speak.start_rec")}
        </motion.button>
      )}

      {/* ═══ STAGE: RECORDING ═══ */}
      {stage === "recording" && (
        <div className="text-center py-4">
          <div className="flex items-center justify-center gap-1.5 h-12 mb-4">
            {waveform.map((h, i) => (
              <motion.div
                key={i}
                animate={{ height: h }}
                transition={{ duration: 0.1 }}
                className="w-1.5 rounded-full bg-gradient-to-t from-rose-500 to-orange-400"
              />
            ))}
          </div>
          <div
            className={`text-4xl font-bold mb-4 tabular-nums ${
              recordLeft <= 10 ? "text-red-600 animate-pulse" : "text-slate-900 dark:text-white"
            }`}
          >
            {formatTime(recordLeft)}
          </div>
          <button
            onClick={stopRecording}
            className="px-8 py-3 rounded-xl bg-slate-800 text-white font-semibold hover:bg-slate-900 transition-colors"
          >
            {t("speak.stop")}
          </button>
        </div>
      )}

      {/* ═══ STAGE: REVIEW ═══ */}
      {stage === "review" && audioUrl && (
        <div className="space-y-4">
          <div className="bg-white/80 dark:bg-slate-800/80 rounded-xl p-4 border border-rose-100 dark:border-slate-700">
            <div className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-2">
              {t("speak.your_answer")}
            </div>
            <audio ref={audioRef} src={audioUrl} controls className="w-full" />
          </div>
          <div className="flex gap-3">
            <button
              onClick={recordAgain}
              className="flex-1 py-3 rounded-xl border-2 border-rose-300 text-rose-600 font-semibold hover:bg-rose-50 transition-colors"
            >
              {t("speak.rerecord")}
            </button>
            <button
              onClick={submitAudio}
              className="flex-1 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold hover:shadow-lg transition-shadow"
            >
              {t("speak.submit")}
            </button>
          </div>
        </div>
      )}

      {/* ═══ STAGE: UPLOADING ═══ */}
      {stage === "uploading" && (
        <div className="text-center py-6">
          <div className="text-slate-600 dark:text-slate-300 mb-3">{t("speak.uploading")}</div>
          <div className="h-2 bg-rose-100 rounded-full overflow-hidden mb-2">
            <div
              className="h-full bg-gradient-to-r from-rose-500 to-orange-500 transition-all"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <div className="text-sm text-slate-500 dark:text-slate-400 tabular-nums">{uploadProgress}%</div>
        </div>
      )}

      {/* ═══ STAGE: DONE ═══ */}
      {stage === "done" && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center py-6"
        >
          <div className="text-5xl mb-3">🎉</div>
          <div className="text-lg font-bold text-emerald-600 mb-1">
            {t("speak.done")}
          </div>
          <div className="text-sm text-slate-500 dark:text-slate-400">
            {t("speak.done_sub")}
          </div>
        </motion.div>
      )}
    </div>
  );
}