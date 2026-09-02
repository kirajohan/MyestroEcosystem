"use client";

import { motion } from "framer-motion";
import { useTheme } from "@/app/providers";

export default function Aurora() {
  const { theme } = useTheme();
  const isDark = theme === "dark";

  // Light mode: och orange → to'q qizil (juda yorqin)
  // Dark mode: to'q qizil → to'q orange (chuqur ranglar)
  const blobs = isDark
    ? [
        { color: "rgba(255, 80, 40, 0.55)", x: 15, y: 20, size: 900, dur: 14 },
        { color: "rgba(220, 38, 38, 0.5)", x: 70, y: 35, size: 1000, dur: 16 },
        { color: "rgba(251, 146, 60, 0.45)", x: 40, y: 70, size: 850, dur: 12 },
        { color: "rgba(249, 115, 22, 0.5)", x: 85, y: 15, size: 950, dur: 18 },
        { color: "rgba(185, 28, 28, 0.4)", x: 50, y: 50, size: 800, dur: 15 },
      ]
    : [
        { color: "rgba(255, 140, 50, 0.6)", x: 15, y: 25, size: 900, dur: 14 },
        { color: "rgba(255, 69, 58, 0.5)", x: 75, y: 40, size: 1000, dur: 16 },
        { color: "rgba(251, 191, 36, 0.5)", x: 45, y: 70, size: 850, dur: 12 },
        { color: "rgba(239, 68, 68, 0.55)", x: 85, y: 20, size: 950, dur: 18 },
        { color: "rgba(249, 115, 22, 0.5)", x: 55, y: 55, size: 800, dur: 15 },
      ];

  return (
    <div className="absolute inset-0 overflow-hidden">
      {/* Base background */}
      <div
        className={`absolute inset-0 transition-colors duration-700 ${
          isDark
            ? "bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950"
            : "bg-gradient-to-br from-orange-50 via-white to-rose-50"
        }`}
      />

      {/* Animated aurora blobs — kattaroq, tezroq, yorqinroq */}
      {blobs.map((blob, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full blur-3xl will-change-transform"
          style={{
            background: `radial-gradient(circle, ${blob.color} 0%, transparent 70%)`,
            width: blob.size,
            height: blob.size,
            left: `${blob.x}%`,
            top: `${blob.y}%`,
            transform: "translate(-50%, -50%)",
          }}
          animate={{
            x: [0, 150, -100, 80, 0],
            y: [0, -120, 100, -60, 0],
            scale: [1, 1.4, 0.8, 1.2, 1],
          }}
          transition={{
            duration: blob.dur,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 1,
          }}
        />
      ))}

      {/* Noise overlay */}
      <div
        className={`absolute inset-0 mix-blend-overlay transition-opacity duration-700 ${
          isDark ? "opacity-[0.04]" : "opacity-[0.02]"
        }`}
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
        }}
      />
    </div>
  );
}