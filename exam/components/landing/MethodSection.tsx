"use client";

import { memo, useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { useLanguage } from "@/app/providers";

const METHOD_CARDS = [
  { icon: "🧠", title: "Active Recall", descKey: "method.c1", color: "from-cyan-500 to-blue-600" },
  { icon: "🔄", title: "Spaced Repetition", descKey: "method.c2", color: "from-purple-500 to-pink-600" },
  { icon: "⚡", title: "Instant AI Feedback", descKey: "method.c3", color: "from-amber-500 to-orange-600" },
  { icon: "🎯", title: "Personalized Path", descKey: "method.c4", color: "from-emerald-500 to-teal-600" },
];

export function MethodSection() {
  const { t } = useLanguage();
  const containerRef = useRef<HTMLDivElement>(null);
  
  // ✨ YANGI: Ko'proq scroll joyi
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start 0.5", "end 0.5"], // ✨ Sekinroq boshlanadi, sekinroq tugaydi
  });

  // Kartalar 25-40% da chiqadi
  const cardsOpacity = useTransform(scrollYProgress, [0.25, 0.4], [0, 1]);
  const cardsY = useTransform(scrollYProgress, [0.25, 0.4], [50, 0]);
  const glassOpacity = useTransform(scrollYProgress, [0, 0.15], [0.3, 1]);

  const fullText = t("method.text");
  const keywords = t("method.keywords").split(",");
  
  const words = fullText.split(" ");

  return (
    <section
      ref={containerRef}
      className="relative h-[100vh]" // ✨ 100vh -> 130vh (ko'proq scroll joyi)
      // iOS/Android'da 100vh brauzer paneli bilan birga hisoblanadi (kontent kesiladi) —
      // dvh qo'llab-quvvatlanmasa inline qiymat e'tiborsiz qoladi va yuqoridagi 100vh ishlaydi
      style={{ height: "100dvh" }}
      id="method"
    >
      {/* Sticky Container */}
      <div
        className="sticky top-0 h-screen flex items-center justify-center px-4 md:px-6"
        style={{ height: "100dvh" }}
      >
        
        {/* Laptop Glass Container */}
        <div className="relative w-full max-w-5xl">
          
          {/* Laptop Frame (3 ta rangli nuqta) */}
          <div className="absolute -top-10 left-6 md:left-8 flex items-center gap-2 z-20">
            <div className="w-2.5 h-2.5 md:w-3 md:h-3 rounded-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]" />
            <div className="w-2.5 h-2.5 md:w-3 md:h-3 rounded-full bg-yellow-500 shadow-[0_0_10px_rgba(234,179,8,0.5)]" />
            <div className="w-2.5 h-2.5 md:w-3 md:h-3 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
          </div>

          {/* Glass Container - Mobile uchun yengilroq */}
          <motion.div
            style={{ opacity: glassOpacity }}
            className="relative rounded-2xl md:rounded-[2.5rem] bg-white/70 dark:bg-slate-900/60 backdrop-blur-md border border-slate-200 dark:border-slate-700/50 p-6 md:p-12 lg:p-16 shadow-2xl overflow-hidden"
          >
            {/* Background Glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-purple-500/5 pointer-events-none" />

            {/* Sarlavha */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-6 md:mb-10 relative z-10"
            >
              <div className="inline-block bg-cyan-100 text-cyan-700 border-cyan-200 dark:bg-cyan-500/20 dark:text-cyan-400 dark:border-cyan-500/30 text-xs md:text-sm font-semibold px-3 md:px-4 py-1.5 md:py-2 rounded-full mb-3 md:mb-4 border">
                {t("method.badge")}
              </div>
              <h2 className="text-2xl md:text-4xl lg:text-5xl font-bold text-slate-900 dark:text-white">
                {t("method.title_a")}
                <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                  {t("method.title_b")}
                </span>
              </h2>
            </motion.div>

            {/* ✨ YANGI: Tezkor Text Reveal - Mobile uchun soddaroq */}
            <div className="relative z-10 text-xl md:text-3xl lg:text-4xl font-bold leading-tight text-center max-w-4xl mx-auto">
              {words.map((word, i) => {
                // ✨ 2 ta so'z bir vaqtda ochiladi (tezroq)
                const groupSize = 2;
                const groupIndex = Math.floor(i / groupSize);
                const totalGroups = Math.ceil(words.length / groupSize);
                
                const start = groupIndex / totalGroups;
                const end = start + 1 / totalGroups;
                const isKeyword = keywords.includes(word.replace(/[.,]/g, ""));

                return (
                  <WordReveal
                    key={i}
                    word={word}
                    range={[start, end]}
                    progress={scrollYProgress}
                    isKeyword={isKeyword}
                  />
                );
              })}
            </div>

            {/* 4 Ustunli Metodika Kartalari */}
            <motion.div
              style={{ opacity: cardsOpacity, y: cardsY }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4 mt-8 md:mt-12 relative z-10"
            >
              {METHOD_CARDS.map((card, idx) => (
                <motion.div
                  key={card.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.1 }}
                  className="group relative bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 rounded-xl md:rounded-2xl p-4 md:p-5 hover:border-cyan-500/50 transition-all duration-300"
                >
                  {/* Gradient Glow on Hover */}
                  <div
                    className={`absolute inset-0 bg-gradient-to-br ${card.color} rounded-xl md:rounded-2xl blur-xl opacity-0 group-hover:opacity-20 transition-opacity duration-300`}
                  />

                  <div className="relative z-10">
                    <div
                      className={`w-10 h-10 md:w-12 md:h-12 rounded-lg md:rounded-xl bg-gradient-to-br ${card.color} flex items-center justify-center text-xl md:text-2xl mb-2 md:mb-3 shadow-lg`}
                    >
                      {card.icon}
                    </div>
                    <h3 className="text-base md:text-lg font-bold text-slate-900 dark:text-white mb-1">
                      {card.title}
                    </h3>
                    <p className="text-xs md:text-sm text-slate-600 dark:text-slate-400">{t(card.descKey)}</p>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

// ✨ YANGI: Mobile uchun soddaroq Word Reveal (blur yo'q)
const WordReveal = memo(function WordReveal({
  word,
  range,
  progress,
  isKeyword,
}: {
  word: string;
  range: [number, number];
  progress: any;
  isKeyword: boolean;
}) {
  // ✨ Faqat opacity (blur mobile'da crash qiladi)
  const opacity = useTransform(progress, range, [0.15, 1]);

  return (
    <motion.span
      style={{ opacity }}
      className={`inline-block mr-2 md:mr-3 mb-2 transition-all duration-300 ${
        isKeyword
          ? "bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent drop-shadow-[0_0_15px_rgba(34,211,238,0.6)]"
          : "text-slate-900 dark:text-white"
      }`}
    >
      {word}
    </motion.span>
  );
});