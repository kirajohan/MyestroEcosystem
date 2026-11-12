"use client";

import Link from "next/link";
import dynamic from "next/dynamic";
import { motion, AnimatePresence } from "framer-motion";
import { useLanguage } from "./providers";
import CurtainEffect from "@/components/landing/CurtaineEffect";
import Header from "@/components/landing/Header";
import {
  HorizontalRoulette,
  KineticHero,
  GlowButton,
  AnimatedCounter,
  FloatingWords,
  InfiniteMarquee,
  // CardStack,
  // QuizCard,
  // TextReveal,
  // AudioWaveform,~
} from "@/components/landing/Sections";

// Hero'dan pastdagi bo'limlar alohida chunk'larda yuklanadi (SSR saqlanadi, birinchi JS yengillashadi)
const Footer = dynamic(() => import("@/components/landing/Footer"));
const FAQ = dynamic(() => import("@/components/landing/FAQ"));
const InteractiveDemoSection = dynamic(() =>
  import("@/components/landing/interactiveDemo").then((m) => m.InteractiveDemoSection)
);
const MethodSection = dynamic(() =>
  import("@/components/landing/MethodSection").then((m) => m.MethodSection)
);
const LearningJourney = dynamic(() =>
  import("@/components/landing/LearningJourney").then((m) => m.LearningJourney)
);

const FEATURES = [
  { id: "listening", icon: "🎧", title: "Listening", color: "from-blue-500 to-cyan-500" },
  { id: "reading", icon: "📖", title: "Reading", color: "from-emerald-500 to-teal-500" },
  { id: "writing", icon: "✍️", title: "Writing", color: "from-amber-500 to-orange-500" },
  { id: "speaking", icon: "🎤", title: "Speaking", color: "from-rose-500 to-pink-500" },
  { id: "ielts", icon: "🇬🇧", title: "IELTS", color: "from-red-500 to-orange-500" },
  { id: "cefr", icon: "🇪🇺", title: "CEFR", color: "from-blue-600 to-indigo-600" },
  { id: "toefl", icon: "🇺🇸", title: "TOEFL", color: "from-green-500 to-emerald-600" },
];

const STATS = [
  { value: 10000, key: "stat.students", suffix: "+" },
  { value: 94, key: "stat.success", suffix: "%" },
  { value: 50, key: "stat.countries", suffix: "+" },
  { value: 4.9, key: "stat.rating", suffix: "★" },
];

const TESTIMONIALS = [
  { name: "John D.", key: "rev.1", rating: 5 },
  { name: "Sarah K.", key: "rev.2", rating: 5 },
  { name: "Mike R.", key: "rev.3", rating: 5 },
  { name: "Anna L.", key: "rev.4", rating: 5 },
];

const FAQ_COUNT = 10;

export default function LandingPage() {
  const { t } = useLanguage();

  const features = FEATURES.map((f) => ({ ...f, desc: t(`feat.${f.id}`) }));
  const faqItems = Array.from({ length: FAQ_COUNT }, (_, i) => ({
    q: t(`faq.${i + 1}.q`),
    a: t(`faq.${i + 1}.a`),
    highlight: t(`faq.${i + 1}.h`),
  }));

  return (
    <main className="min-h-screen min-h-[100dvh] overflow-x-hidden supports-[overflow:clip]:overflow-x-clip relative">
      <CurtainEffect />
      <Header />

      {/* ═══ HERO ═══ */}
      <section className="relative max-w-7xl mx-auto px-6 py-20 md:py-32">
        <FloatingWords />
        <div className="relative z-10 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.5 }}
            className="inline-flex items-center gap-2 border border-orange-200 dark:border-orange-500/30 bg-orange-50 dark:bg-orange-500/10 text-orange-700 dark:text-orange-400 text-sm font-semibold px-4 py-2 rounded-full mb-8"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-500" />
            </span>
            {t("hero_badge")}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.6 }}
          >
            <KineticHero />
          </motion.div>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.7 }}
            className="text-base-secondary text-lg md:text-xl max-w-2xl mx-auto mb-10"
          >
            {t("hero_subtitle")}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.8 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <GlowButton href="/login">🚀 {t("cta_start")}</GlowButton>
            <Link
              href="#features"
              className="px-8 py-4 text-lg font-semibold rounded-xl bg-slate-100 dark:bg-white/10 hover:bg-slate-200 dark:hover:bg-white/20 text-base-primary backdrop-blur transition-colors"
            >
              {t("cta_learn")}
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-20 max-w-3xl mx-auto"
          >
            {STATS.map((stat) => (
              <div key={stat.key} className="text-center">
                <div className="text-3xl md:text-4xl font-bold bg-gradient-to-br from-orange-500 to-rose-500 bg-clip-text text-transparent">
                  <AnimatedCounter value={stat.value} suffix={stat.suffix} />
                </div>
                <div className="text-base-secondary text-sm mt-1">
                  {t(stat.key)}
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ═══ MARQUEE ═══ */}
      <InfiniteMarquee
        items={["Grammar", "Vocabulary", "Speaking", "Listening", "Writing", "Reading", "IELTS", "Business English", "Pronunciation", "Idioms"]}
      />

      {/* ═══ FEATURES (Faqat HorizontalRoulette) ═══ */}
      <section id="features" className="relative py-24 overflow-hidden">
        <div className="max-w-7xl mx-auto px-6 mb-12 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4 text-slate-900 dark:text-white">
              {t("feat.title_a")}
              <span className="bg-gradient-to-r from-orange-500 to-rose-500 bg-clip-text text-transparent">
                {t("feat.title_b")}
              </span>
            </h2>
            <p className="text-slate-600 dark:text-slate-400 text-lg max-w-2xl mx-auto">
              {t("feat.sub")}
            </p>
          </motion.div>
        </div>
        
        {/* Faqat HorizontalRoulette, ichida RouletteCard va SpotlightCard ishlaydi */}
        <HorizontalRoulette items={features} />
      </section>

      {/* ═══ DEMO ═══ */}
          
          <InteractiveDemoSection />
          
      {/* ═══ METHOD (Yangi) ═══ */}
  
          <MethodSection />

      {/* ═══ BEFORE/AFTER ═══ */}
      {/* ═══ LEARNING JOURNEY TIMELINE ═══ */}
          <LearningJourney />

      {/* ═══ TESTIMONIALS ═══ */}
      <section className="relative py-24 max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-base-primary text-4xl md:text-5xl font-bold">
            {t("rev.title_a")}
            <span className="text-gradient-brand">{t("rev.title_b")}</span>
            {t("rev.title_c")}
          </h2>
        </motion.div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <AnimatePresence>
            {TESTIMONIALS.map((item, i) => (
              <motion.div
                key={item.name}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, type: "spring" }}
                whileHover={{ y: -5 }}
                className="card rounded-2xl p-6"
              >
                <div className="flex mb-3 text-orange-500">{"★".repeat(item.rating)}</div>
                <p className="text-base-secondary mb-4">"{t(item.key)}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-500 to-rose-500" />
                  <div>
                    <div className="text-base-primary font-semibold">{item.name}</div>
                    <div className="text-base-muted text-xs">{t("rev.role")}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </section>

      {/* ═══ FAQ ═══ */}
      <FAQ items={faqItems} />

      {/* ═══ CTA ═══ */}
      <section className="relative py-24 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-600 via-orange-500 to-rose-500" />
        <div className="relative max-w-4xl mx-auto px-6 text-center">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-4xl md:text-6xl font-bold text-white mb-6"
          >
            {t("cta.title")}
          </motion.h2>
          <p className="text-xl text-white/90 mb-10">
            {t("cta.sub")}
          </p>
          <Link
            href="/login"
            className="inline-flex items-center gap-2 bg-white text-orange-600 text-xl font-bold px-10 py-5 rounded-xl hover:bg-orange-50 transition-colors shadow-2xl"
          >
            {t("cta.btn")}
          </Link>
        </div>
      </section>

      <Footer />
    </main>
  );
}