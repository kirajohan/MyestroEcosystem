"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { API_URL } from "@/lib/api";
import { useLanguage } from "@/app/providers";

interface AudioPlayerProps {
  audioUrl: string;
  maxListens?: number;
  title?: string;
}

export default function AudioPlayer({
  audioUrl,
  maxListens = 3,
  title,
}: AudioPlayerProps) {
  const { t } = useLanguage();
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [speed, setSpeed] = useState(1);
  const [listenCount, setListenCount] = useState(0);
  const [waveformBars, setWaveformBars] = useState<number[]>([]);

  // Full URL yaratish
  const fullAudioUrl = `${API_URL}${audioUrl}`;

  // Generate fake waveform data
  useEffect(() => {
    const bars = Array.from({ length: 60 }, () => 0.2 + Math.random() * 0.8);
    setWaveformBars(bars);
  }, [fullAudioUrl]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleEnded = () => {
      setIsPlaying(false);
      setListenCount((c) => c + 1);
    };

    audio.addEventListener("timeupdate", updateTime);
    audio.addEventListener("loadedmetadata", updateDuration);
    audio.addEventListener("play", handlePlay);
    audio.addEventListener("pause", handlePause);
    audio.addEventListener("ended", handleEnded);

    return () => {
      audio.removeEventListener("timeupdate", updateTime);
      audio.removeEventListener("loadedmetadata", updateDuration);
      audio.removeEventListener("play", handlePlay);
      audio.removeEventListener("pause", handlePause);
      audio.removeEventListener("ended", handleEnded);
    };
  }, []);

  const togglePlay = async () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (listenCount >= maxListens) {
      alert(t("audio.limit_alert", { n: maxListens }));
      return;
    }

    if (isPlaying) {
      audio.pause();
    } else {
      await audio.play();
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current;
    if (!audio) return;
    const newTime = Number(e.target.value);
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleSpeedChange = (newSpeed: number) => {
    const audio = audioRef.current;
    if (audio) audio.playbackRate = newSpeed;
    setSpeed(newSpeed);
  };

  const formatTime = (t: number) => {
    if (isNaN(t)) return "0:00";
    const m = Math.floor(t / 60);
    const s = Math.floor(t % 60);
    return `${m}:${String(s).padStart(2, "0")}`;
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;
  const canListen = listenCount < maxListens;
  const speeds = [0.75, 1, 1.25, 1.5];

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6 shadow-2xl border border-white/10 backdrop-blur-xl">
      {/* Background glow */}
      <div className="absolute inset-0 opacity-30 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-64 h-64 bg-orange-500 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-rose-500 rounded-full blur-3xl" />
      </div>

      <audio ref={audioRef} src={fullAudioUrl} preload="metadata" />

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <div className="text-xs uppercase tracking-widest text-orange-400 font-semibold mb-1">
              {t("audio.task")}
            </div>
            <h3 className="text-xl font-bold text-white">{title || t("audio.default_title")}</h3>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-400">{t("audio.listens")}</div>
            <div className={`text-sm font-bold ${canListen ? "text-white" : "text-red-400"}`}>
              {listenCount} / {maxListens}
            </div>
          </div>
        </div>

        {/* Vinyl Disc + Waveform */}
        <div className="flex items-center gap-6 mb-6">
          {/* Vinyl Disc */}
          <div className="relative flex-shrink-0">
            <motion.div
              className="relative w-24 h-24 rounded-full bg-gradient-to-br from-slate-700 via-slate-900 to-black shadow-2xl flex items-center justify-center"
              animate={{ rotate: isPlaying ? 360 : 0 }}
              transition={{
                duration: 3,
                repeat: isPlaying ? Infinity : 0,
                ease: "linear",
              }}
            >
              {/* Vinyl grooves */}
              {[20, 30, 40, 50, 60, 70].map((size) => (
                <div
                  key={size}
                  className="absolute rounded-full border border-white/5"
                  style={{
                    width: `${size}%`,
                    height: `${size}%`,
                  }}
                />
              ))}
              {/* Center */}
              <div className="relative w-10 h-10 rounded-full bg-gradient-to-br from-orange-500 to-rose-500 flex items-center justify-center shadow-lg">
                <div className="w-2 h-2 rounded-full bg-white" />
              </div>
              {/* Glow pulse when playing */}
              {isPlaying && (
                <motion.div
                  className="absolute inset-0 rounded-full bg-orange-500/30"
                  animate={{ scale: [1, 1.3, 1], opacity: [0.5, 0, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              )}
            </motion.div>
          </div>

          {/* Waveform Visualizer */}
          <div className="flex-1 flex items-center gap-0.5 h-20">
            {waveformBars.map((height, i) => {
              const barProgress = (i / waveformBars.length) * 100;
              const isPlayed = barProgress <= progress;
              const isActive = isPlaying && Math.abs(barProgress - progress) < 3;

              return (
                <motion.div
                  key={i}
                  className="flex-1 rounded-full transition-all"
                  style={{
                    background: isPlayed
                      ? "linear-gradient(to top, #f97316, #fb7185)"
                      : "rgba(255,255,255,0.1)",
                  }}
                  animate={{
                    height: isActive
                      ? `${height * 100 * (0.7 + Math.random() * 0.3)}%`
                      : `${height * (isPlayed ? 80 : 40)}%`,
                    boxShadow: isActive ? "0 0 10px #f97316" : "none",
                  }}
                  transition={{
                    duration: isActive ? 0.2 : 0.3,
                    ease: "easeOut",
                  }}
                />
              );
            })}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="relative mb-4">
          <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-orange-500 to-rose-500 rounded-full"
              style={{ width: `${progress}%` }}
              transition={{ duration: 0.1 }}
            />
          </div>
          <input
            type="range"
            min={0}
            max={duration || 0}
            value={currentTime}
            onChange={handleSeek}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <div className="flex justify-between text-xs text-slate-400 mt-2">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between gap-4">
          {/* Play/Pause Button */}
          <motion.button
            onClick={togglePlay}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={!canListen}
            className={`relative w-16 h-16 rounded-full flex items-center justify-center shadow-2xl transition-all ${
              canListen
                ? "bg-gradient-to-br from-orange-500 to-rose-500 hover:shadow-orange-500/50"
                : "bg-slate-700 cursor-not-allowed"
            }`}
          >
            <AnimatePresence mode="wait">
              {isPlaying ? (
                <motion.svg
                  key="pause"
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0, opacity: 0 }}
                  className="w-6 h-6 text-white"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                </motion.svg>
              ) : (
                <motion.svg
                  key="play"
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0, opacity: 0 }}
                  className="w-6 h-6 text-white ml-1"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M8 5v14l11-7z" />
                </motion.svg>
              )}
            </AnimatePresence>
          </motion.button>

          {/* Speed Controller */}
          <div className="flex items-center gap-1 bg-white/5 backdrop-blur-sm rounded-xl p-1 border border-white/10">
            {speeds.map((s) => (
              <motion.button
                key={s}
                onClick={() => handleSpeedChange(s)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`relative px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                  speed === s
                    ? "bg-gradient-to-r from-orange-500 to-rose-500 text-white shadow-lg"
                    : "text-slate-300 hover:text-white"
                }`}
              >
                {s}x
              </motion.button>
            ))}
          </div>

          {/* Max listens warning */}
          {!canListen && (
            <motion.div
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-xs text-red-400 font-semibold"
            >
              {t("audio.limit")}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}