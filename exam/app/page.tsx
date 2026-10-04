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
  // Asosiy Ko'nikmalar
  { 
    icon: "🎧", 
    title: "Listening", 
    desc: "Haqiqiy audio materiallar orqali tinglab tushunishni rivojlantiring.", 
    color: "from-blue-500 to-cyan-500" 
  },
  { 
    icon: "📖", 
    title: "Reading", 
    desc: "Qiziqarli matnlar bilan so'z boyligingizni oshiring.", 
    color: "from-emerald-500 to-teal-500" 
  },
  { 
    icon: "✍️", 
    title: "Writing", 
    desc: "AI yordamida insholaringizni tekshirtiring va grammatikani to'g'rilang.", 
    color: "from-amber-500 to-orange-500" 
  },
  { 
    icon: "🎤", 
    title: "Speaking", 
    desc: "Ovozli suhbatlar orqali talaffuzingizni mukammallashtiring.", 
    color: "from-rose-500 to-pink-500" 
  },
  // Xalqaro Standartlar
  { 
    icon: "🇬🇧", 
    title: "IELTS", 
    desc: "Academic va General Training uchun maxsus tayyorgarlik va strategiyalar.", 
    color: "from-red-500 to-orange-500" 
  },
  { 
    icon: "🇪🇺", 
    title: "CEFR", 
    desc: "A1 dan C2 gacha Yevropa standartlari bo'yicha aniq baholash tizimi.", 
    color: "from-blue-600 to-indigo-600" 
  },
  { 
    icon: "🇺🇸", 
    title: "TOEFL", 
    desc: "Amerika universitetlari uchun iBT formatida puxta mashqlar.", 
    color: "from-green-500 to-emerald-600" 
  },
];

const STATS = [
  { value: 10000, label: "Talabalar", suffix: "+" },
  { value: 94, label: "Muvaffaqiyat", suffix: "%" },
  { value: 50, label: "Davlatlar", suffix: "+" },
  { value: 4.9, label: "Reyting", suffix: "★" },
];

const TESTIMONIALS = [
  { name: "John D.", text: "Lorem ipsum dolor sit amet.", rating: 5 },
  { name: "Sarah K.", text: "Consectetur adipiscing elit.", rating: 5 },
  { name: "Mike R.", text: "Sed do eiusmod tempor.", rating: 5 },
  { name: "Anna L.", text: "Ut enim ad minim veniam.", rating: 5 },
];

const FAQ_ITEMS = [
  { 
    q: "🚀 Myestro nima va qanday ishlaydi?", 
    a: "Myestro — bu AI yordamida ingliz tilini o'rganish platformasi. Siz Telegram bot orqali AI o'qituvchi bilan suhbatlashasiz, imtihonlar topshirasiz va o'z progressingizni kuzatasiz.",
    highlight: "💡 AI sizning xatolaringizni darhol tuzatadi va tushuntiradi."
  },
  { 
    q: "🎯 Qanday darajadagilar uchun mos?", 
    a: "Platforma boshlang'ich (A1) dan yuqori (C1) darajagacha bo'lgan barcha foydalanuvchilar uchun mo'ljallangan. Ro'yxatdan o'tishda sizning darajangiz aniqlanadi va shunga mos kontent taqdim etiladi.",
    highlight: "📊 CEFR standartlari bo'yicha A1, A2, B1, B2, C1 darajalari mavjud."
  },
  { 
    q: "💰 Narxlari qanday va qanday to'lash mumkin?", 
    a: "Hozirda platforma bepul beta-versiyada ishlaydi. Kelajakda oylik obuna modellari joriy etiladi. To'lovlar Click, Payme va xalqaro kartalar orqali amalga oshiriladi.",
    highlight: "🎁 Hozir ro'yxatdan o'ting va birinchi 3 oy bepul foydalaning!"
  },
  { 
    q: "🤖 AI qanday yordam beradi?", 
    a: "AI o'qituvchi sizning har bir xatongizni tahlil qiladi, grammatik tuzatishlar kiritadi, yangi so'zlar taklif qiladi va shaxsiylashtirilgan mashqlar beradi. Bu xuddi shaxsiy repetitor bilan ishlashga o'xshaydi.",
    highlight: "⚡ AI 24/7 ishlaydi va istalgan vaqtda yordam berishga tayyor."
  },
  { 
    q: "📱 Qanday qurilmalarda ishlaydi?", 
    a: "Platforma Telegram bot orqali ishlagani uchun istalgan qurilmada (telefon, planshet, kompyuter) ishlaydi. Internet ulanishi bo'lsa bas.",
    highlight: "🌍 Qayerda bo'lsangiz ham o'rganishingiz mumkin."
  },
  { 
    q: "📊 Natijalarimni qanday kuzataman?", 
    a: "Shaxsiy kabintingizda barcha imtihon natijalaringiz, progressingiz va CEFR darajangiz o'zgarishi ko'rsatiladi. Haftalik va oylik hisobotlar ham mavjud.",
    highlight: "📈 Har hafta progressingizni ko'rib, motivatsiyangiz oshadi."
  },
  { 
    q: "🎓 Sertifikat berasizlarmi?", 
    a: "Hozircha rasmiy sertifikat berilmaydi, lekin kelajakda IELTS va CEFR standartlariga mos sertifikatlar joriy etiladi. Hozircha sizning natijalaringiz va progressingiz platformada saqlanadi.",
    highlight: "🏆 Kelajakda xalqaro e'tirof etilgan sertifikatlar rejalashtirilgan."
  },
  { 
    q: "🔒 Ma'lumotlarim xavfsizmi?", 
    a: "Ha, barcha ma'lumotlar shifrlangan holda saqlanadi. Biz GDPR va maxfiylik siyosatiga qat'iy rioya qilamiz. Sizning ma'lumotlaringiz faqat sizga xizmat ko'rsatish uchun ishlatiladi.",
    highlight: "🛡️ Ma'lumotlaringiz to'liq himoyalangan va uchinchi tomonlarga berilmaydi."
  },
  { 
    q: "👥 Guruh darslari bormi?", 
    a: "Hozircha faqat individual AI o'qituvchi bilan ishlash mavjud. Kelajakda guruh darslari va jonli darslar qo'shiladi.",
    highlight: "🤝 Guruh darslari 2025-yilda joriy etiladi."
  },
  { 
    q: "❓ Yana savollarim bo'lsa, kimga murojaat qilaman?", 
    a: "Bot orqali admin bilan bog'lanishingiz mumkin. Shuningdek, Telegram kanalimizda yangiliklar va yordam materiallari mavjud.",
    highlight: "💬 @myestro_support — biz doimo yordam berishga tayyormiz!"
  }
];

export default function LandingPage() {
  const { t } = useLanguage();

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
              <div key={stat.label} className="text-center">
                <div className="text-3xl md:text-4xl font-bold bg-gradient-to-br from-orange-500 to-rose-500 bg-clip-text text-transparent">
                  <AnimatedCounter value={stat.value} suffix={stat.suffix} />
                </div>
                <div className="text-base-secondary text-sm mt-1">
                  {stat.label}
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
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Barcha imkoniyatlar{" "}
              <span className="bg-gradient-to-r from-orange-500 to-rose-500 bg-clip-text text-transparent">
                bir joyda
              </span>
            </h2>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto">
              Myestro platformasi sizning ingliz tili bilimingizni yangi bosqichga olib chiqadi.
            </p>
          </motion.div>
        </div>
        
        {/* Faqat HorizontalRoulette, ichida RouletteCard va SpotlightCard ishlaydi */}
        <HorizontalRoulette items={FEATURES} />
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
            Minglab <span className="text-gradient-brand">talabalar</span> sevgan
          </h2>
        </motion.div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <AnimatePresence>
            {TESTIMONIALS.map((t, i) => (
              <motion.div
                key={t.name}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, type: "spring" }}
                whileHover={{ y: -5 }}
                className="card rounded-2xl p-6"
              >
                <div className="flex mb-3 text-orange-500">{"★".repeat(t.rating)}</div>
                <p className="text-base-secondary mb-4">"{t.text}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-500 to-rose-500" />
                  <div>
                    <div className="text-base-primary font-semibold">{t.name}</div>
                    <div className="text-base-muted text-xs">Talaba</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </section>

      {/* ═══ FAQ ═══ */}
      <FAQ items={FAQ_ITEMS} />

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
            Ingliz tilini mukammal bilishga tayyormisiz?
          </motion.h2>
          <p className="text-xl text-white/90 mb-10">
            Telegram orqali kirib, birinchi imtihoningizni topshiring.
          </p>
          <Link
            href="/login"
            className="inline-flex items-center gap-2 bg-white text-orange-600 text-xl font-bold px-10 py-5 rounded-xl hover:bg-orange-50 transition-colors shadow-2xl"
          >
            🚀 Bepul boshlash
          </Link>
        </div>
      </section>

      <Footer />
    </main>
  );
}