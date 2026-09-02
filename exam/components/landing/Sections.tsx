"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence, useScroll, useTransform, useInView, MotionValue } from "framer-motion";
import { useTheme } from "@/app/providers";

// ═══════════════════════════════════════════════════════════
// KINETIC HERO — Rotating words with blur effect
// ═══════════════════════════════════════════════════════════

const ROTATING_WORDS = [
  "Interactive Stories",
  "AI Practice",
  "Live Conversations",
  "Real Exams",
];

export function KineticHero() {
  const [wordIndex, setWordIndex] = useState(0);
  const { theme } = useTheme();
  const isDark = theme === "dark";

  useEffect(() => {
    const interval = setInterval(() => {
      setWordIndex((i) => (i + 1) % ROTATING_WORDS.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <h1
      className={`text-4xl md:text-6xl lg:text-7xl font-bold leading-tight mb-6 ${
        isDark ? "text-white" : "text-slate-900"
      }`}
    >
      Master English through
      <br />
      <span className="inline-block relative h-[1.2em] overflow-hidden align-bottom">
        <AnimatePresence mode="wait">
          <motion.span
            key={wordIndex}
            initial={{ y: 40, opacity: 0, filter: "blur(10px)" }}
            animate={{ y: 0, opacity: 1, filter: "blur(0px)" }}
            exit={{ y: -40, opacity: 0, filter: "blur(10px)" }}
            transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            className="inline-block bg-gradient-to-r from-orange-600 to-rose-500 bg-clip-text text-transparent"
          >
            {ROTATING_WORDS[wordIndex]}
          </motion.span>
        </AnimatePresence>
      </span>
    </h1>
  );
}

// ═══════════════════════════════════════════════════════════
// SPOTLIGHT CARD — Cursor tracking gradient
// ═══════════════════════════════════════════════════════════

interface SpotlightCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: "dark" | "light" | "auto";
}

export function SpotlightCard({
  children,
  className = "",
  variant = "dark",
}: SpotlightCardProps) {
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const ref = useRef<HTMLDivElement>(null);
  const [hover, setHover] = useState(false);
  const { theme } = useTheme();
  const isDark = theme === "dark";

  const handleMouse = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    setPos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  };

  // Variant bo'yicha fon rangini aniqlash
  const bgClass =
    variant === "auto"
      ? isDark
        ? "bg-slate-900"
        : "bg-white border border-slate-200"
      : variant === "dark"
      ? "bg-slate-900"
      : "bg-white border border-slate-200";

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouse}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      className={`relative overflow-hidden rounded-2xl ${bgClass} ${className}`}
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <div
        className="pointer-events-none absolute inset-0 transition-opacity duration-300"
        style={{
          opacity: hover ? 1 : 0,
          background: `radial-gradient(600px circle at ${pos.x}px ${pos.y}px, rgba(251,146,60,0.15), transparent 40%)`,
        }}
      />
      <div className="relative z-10 h-full">{children}</div>
      <div className="absolute inset-0 rounded-2xl ring-1 ring-inset ring-white/10" />
    </motion.div>
  );
}

// ═══════════════════════════════════════════════════════════
// GLOW BUTTON — Animated border beam
// ═══════════════════════════════════════════════════════════

interface GlowButtonProps {
  children: React.ReactNode;
  href?: string;
  className?: string;
  onClick?: () => void;
}

export function GlowButton({
  children,
  href,
  className = "",
  onClick,
}: GlowButtonProps) {
  const inner = (
    <motion.div
      className={`relative group ${className}`}
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="absolute -inset-0.5 bg-gradient-to-r from-orange-500 via-amber-400 to-orange-600 rounded-xl opacity-75 blur-sm group-hover:opacity-100 transition duration-500" />
      <div className="relative flex items-center justify-center px-8 py-4 bg-orange-600 rounded-xl text-white font-bold text-lg overflow-hidden">
        <motion.div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              "linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent)",
            width: "40%",
            height: "100%",
            top: 0,
          }}
          animate={{ left: ["-40%", "140%"] }}
          transition={{ duration: 2.5, repeat: Infinity, ease: "linear" }}
        />
        <span className="relative z-10">{children}</span>
      </div>
    </motion.div>
  );

  if (href) {
    return <Link href={href}>{inner}</Link>;
  }

  return (
    <button onClick={onClick} className="cursor-pointer">
      {inner}
    </button>
  );
}

// ═══════════════════════════════════════════════════════════
// ANIMATED COUNTER
// ═══════════════════════════════════════════════════════════

interface AnimatedCounterProps {
  value: number;
  suffix?: string;
  duration?: number;
}

export function AnimatedCounter({
  value,
  suffix = "",
  duration = 1500,
}: AnimatedCounterProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once: true });
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    if (!isInView) return;

    const steps = 40;
    const stepTime = duration / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += value / steps;
      if (current >= value) {
        setDisplay(value);
        clearInterval(timer);
      } else {
        setDisplay(Math.floor(current));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [isInView, value, duration]);

  return (
    <span ref={ref} className="tabular-nums">
      {display.toLocaleString()}
      {suffix}
    </span>
  );
}

// ═══════════════════════════════════════════════════════════
// FLOATING WORDS — Background decoration
// ═══════════════════════════════════════════════════════════

const FLOATING_WORDS = [
  "Grammar",
  "Vocabulary",
  "IELTS",
  "CEFR",
  "Fluency",
  "Accent",
  "Speaking",
  "Writing",
  "Reading",
];

export function FloatingWords() {
  const { theme } = useTheme();
  const isDark = theme === "dark";

  return (
    <div
      className="absolute inset-0 overflow-hidden pointer-events-none"
      aria-hidden="true"
    >
      {FLOATING_WORDS.map((word, i) => (
        <motion.div
          key={word}
          className={`absolute text-sm md:text-base font-medium ${
            isDark ? "text-orange-500/20" : "text-orange-200/30"
          }`}
          style={{
            left: `${(i * 13) % 90}%`,
            top: `${(i * 17) % 85}%`,
          }}
          animate={{
            y: [0, -20, 0],
            x: [0, 10, 0],
            rotate: [0, 5, 0],
          }}
          transition={{
            duration: 4 + i * 0.5,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.3,
          }}
        >
          {word}
        </motion.div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// INFINITE MARQUEE
// ═══════════════════════════════════════════════════════════

interface InfiniteMarqueeProps {
  items: string[];
  speed?: number;
}

export function InfiniteMarquee({ items, speed = 30 }: InfiniteMarqueeProps) {
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const duplicatedItems = [...items, ...items];

  return (
    <div
      className={`relative overflow-hidden py-6 ${
        isDark
          ? "bg-slate-900/50"
          : "bg-gradient-to-r from-orange-50 via-white to-orange-50"
      }`}
    >
      <div
        className={`absolute left-0 top-0 bottom-0 w-20 z-10 ${
          isDark
            ? "bg-gradient-to-r from-slate-950 to-transparent"
            : "bg-gradient-to-r from-white to-transparent"
        }`}
      />
      <div
        className={`absolute right-0 top-0 bottom-0 w-20 z-10 ${
          isDark
            ? "bg-gradient-to-l from-slate-950 to-transparent"
            : "bg-gradient-to-l from-white to-transparent"
        }`}
      />
      <motion.div
        className="flex gap-8 whitespace-nowrap"
        animate={{ x: ["0%", "-50%"] }}
        transition={{ duration: speed, repeat: Infinity, ease: "linear" }}
      >
        {duplicatedItems.map((item, i) => (
          <div
            key={`${item}-${i}`}
            className={`flex items-center gap-2 font-medium text-lg ${
              isDark ? "text-slate-400" : "text-slate-500"
            }`}
          >
            <span className="text-orange-500">●</span>
            {item}
          </div>
        ))}
      </motion.div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// CARD STACK — Interactive swipe demo
// ═══════════════════════════════════════════════════════════

const FLASHCARDS = [
  {
    word: "Serendipity",
    meaning: "Happy accident",
    color: "from-orange-500 to-rose-500",
  },
  {
    word: "Eloquent",
    meaning: "Fluent & persuasive",
    color: "from-amber-500 to-orange-500",
  },
  {
    word: "Ephemeral",
    meaning: "Short-lived",
    color: "from-orange-600 to-amber-500",
  },
  {
    word: "Ubiquitous",
    meaning: "Found everywhere",
    color: "from-rose-500 to-orange-500",
  },
];

export function CardStack() {
  const [current, setCurrent] = useState(0);
  const [direction, setDirection] = useState(0);

  const swipe = (dir: number) => {
    setDirection(dir);
    setTimeout(() => {
      setCurrent((c) => (c + 1) % FLASHCARDS.length);
      setDirection(0);
    }, 300);
  };

  const card = FLASHCARDS[current];

  return (
    <div className="relative h-72 w-full max-w-sm mx-auto">
      <AnimatePresence>
        <motion.div
          key={current}
          initial={{ scale: 0.8, opacity: 0, rotate: direction * 10 }}
          animate={{
            scale: 1,
            opacity: 1,
            rotate: 0,
            x: direction * 400,
          }}
          exit={{ scale: 0.8, opacity: 0, x: direction * 400 }}
          transition={{ type: "spring", stiffness: 300, damping: 25 }}
          className={`absolute inset-0 rounded-3xl bg-gradient-to-br ${card.color} p-8 shadow-2xl flex flex-col justify-between text-white`}
        >
          <div className="text-sm opacity-80">Word of the Day</div>
          <div>
            <div className="text-3xl font-bold mb-2">{card.word}</div>
            <div className="text-lg opacity-90">{card.meaning}</div>
          </div>
          <div className="flex justify-between">
            <button
              onClick={() => swipe(-1)}
              className="w-12 h-12 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center text-2xl transition-colors"
              aria-label="Previous card"
            >
              ←
            </button>
            <button
              onClick={() => swipe(1)}
              className="w-12 h-12 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center text-2xl transition-colors"
              aria-label="Next card"
            >
              →
            </button>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// QUIZ CARD — 3D flip card
// ═══════════════════════════════════════════════════════════

export function QuizCard() {
  const [flipped, setFlipped] = useState(false);

  return (
    <div
      className="relative h-64 w-full max-w-sm mx-auto"
      style={{ perspective: "1000px" }}
    >
      <motion.button
        className="relative w-full h-full cursor-pointer focus:outline-none"
        animate={{ rotateY: flipped ? 180 : 0 }}
        transition={{ duration: 0.6 }}
        style={{ transformStyle: "preserve-3d" }}
        onClick={() => setFlipped(!flipped)}
        aria-label={flipped ? "Show question" : "Show answer"}
      >
        {/* Front */}
        <div
          className="absolute inset-0 rounded-2xl bg-gradient-to-br from-orange-500 to-rose-500 p-8 flex flex-col justify-between text-white shadow-xl text-left"
          style={{ backfaceVisibility: "hidden" }}
        >
          <div className="text-xs opacity-80">MINI QUIZ</div>
          <div className="text-xl font-bold">
            Choose the correct: "She ___ to the store yesterday."
          </div>
          <div className="text-sm opacity-80">Tap to reveal answer</div>
        </div>
        {/* Back */}
        <div
          className="absolute inset-0 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 p-8 flex flex-col justify-center text-white shadow-xl text-left"
          style={{ backfaceVisibility: "hidden", transform: "rotateY(180deg)" }}
        >
          <div className="text-xs opacity-80 mb-2">ANSWER</div>
          <div className="text-2xl font-bold mb-3">went ✅</div>
          <div className="text-sm opacity-90">
            Use Past Simple for completed actions in the past.
          </div>
        </div>
      </motion.button>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// FAQ ITEM — Accordion
// ═══════════════════════════════════════════════════════════

interface FAQItemProps {
  q: string;
  a: string;
}

export function FAQItem({ q, a }: FAQItemProps) {
  const [open, setOpen] = useState(false);
  const { theme } = useTheme();
  const isDark = theme === "dark";

  return (
    <motion.div
      className={`border-b ${isDark ? "border-slate-800" : "border-slate-200"}`}
      layout
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full py-5 flex items-center justify-between text-left gap-4"
        aria-expanded={open}
      >
        <span
          className={`font-semibold text-lg ${
            isDark ? "text-white" : "text-slate-900"
          }`}
        >
          {q}
        </span>
        <motion.span
          animate={{ rotate: open ? 45 : 0 }}
          transition={{ duration: 0.2 }}
          className="text-2xl text-orange-600 font-light flex-shrink-0"
          aria-hidden="true"
        >
          +
        </motion.span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
            className="overflow-hidden"
          >
            <p
              className={`pb-5 ${
                isDark ? "text-slate-400" : "text-slate-600"
              }`}
            >
              {a}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ═══════════════════════════════════════════════════════════
// TEXT REVEAL — Scroll reveal text
// ═══════════════════════════════════════════════════════════

interface TextRevealProps {
  text: string;
}

export function TextReveal({ text }: TextRevealProps) {
  const ref = useRef<HTMLParagraphElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start 0.8", "end 0.2"],
  });
  const { theme } = useTheme();
  const isDark = theme === "dark";

  const words = text.split(" ");

  return (
    <p
      ref={ref}
      className={`text-3xl md:text-5xl font-bold leading-tight text-center max-w-4xl mx-auto ${
        isDark ? "text-white" : "text-slate-900"
      }`}
    >
      {words.map((word, i) => {
        const start = i / words.length;
        const end = start + 1 / words.length;
        return (
          <Word key={i} word={word} range={[start, end]} progress={scrollYProgress} />
        );
      })}
    </p>
  );
}

interface WordProps {
  word: string;
  range: [number, number];
  progress: MotionValue<number>;
}

function Word({ word, range, progress }: WordProps) {
  const opacity = useTransform(progress, range, [0.2, 1]);

  return (
    <motion.span style={{ opacity }} className="inline-block mr-3">
      {word}
    </motion.span>
  );
}

// ═══════════════════════════════════════════════════════════
// COMPARE SLIDER — Before/After
// ═══════════════════════════════════════════════════════════

export function CompareSlider() {
  const [pos, setPos] = useState(50);

  return (
    <div className="relative max-w-2xl mx-auto rounded-2xl overflow-hidden shadow-2xl aspect-video bg-slate-100">
      {/* Before */}
      <div className="absolute inset-0 p-8 flex items-center">
        <div className="text-slate-600">
          <div className="text-xs mb-2 font-semibold">BEFORE</div>
          <p className="text-lg">
            I go to Samarkand last year and see many beautiful place.
          </p>
        </div>
      </div>

      {/* After */}
      <motion.div
        className="absolute inset-0 p-8 bg-gradient-to-br from-orange-500 to-rose-500 text-white flex items-center"
        style={{ clipPath: `inset(0 ${100 - pos}% 0 0)` }}
      >
        <div>
          <div className="text-xs mb-2 font-semibold">AFTER</div>
          <p className="text-lg">
            I went to Samarkand last year and saw many beautiful places.
          </p>
        </div>
      </motion.div>

      {/* Range input */}
      <input
        type="range"
        min={0}
        max={100}
        value={pos}
        onChange={(e) => setPos(Number(e.target.value))}
        className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize"
        aria-label="Compare slider"
      />

      {/* Divider */}
      <div
        className="absolute top-0 bottom-0 w-1 bg-white shadow-xl pointer-events-none"
        style={{ left: `${pos}%` }}
      >
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-white shadow-xl flex items-center justify-center text-orange-600 font-bold">
          ⇆
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// AUDIO WAVEFORM — Speaking visualization
// ═══════════════════════════════════════════════════════════

interface AudioWaveformProps {
  barCount?: number;
}

export function AudioWaveform({ barCount = 20 }: AudioWaveformProps) {
  return (
    <div className="flex items-end gap-1 h-12" aria-hidden="true">
      {Array.from({ length: barCount }).map((_, i) => (
        <motion.div
          key={i}
          className="w-1.5 bg-gradient-to-t from-orange-600 to-amber-400 rounded-full"
          animate={{
            height: ["20%", "100%", "40%", "80%", "20%"],
          }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            delay: i * 0.05,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}