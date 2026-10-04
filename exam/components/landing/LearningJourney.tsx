"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const JOURNEY_STEPS = [
  {
    level: "A1",
    title: "Beginner",
    duration: "2-3 oy",
    icon: "🌱",
    description: "Ingliz tilining asoslari: alifbo, oddiy so'zlar, kundalik iboralar.",
    skills: ["O'zingizni tanishtirish", "Raqamlar va ranglar", "Oddiy savollar berish", "Kundalik iboralar"],
  },
  {
    level: "A2",
    title: "Elementary",
    duration: "3-4 oy",
    icon: "🌿",
    description: "Oddiy muloqot, kundalik vaziyatlar, qisqa matnlarni tushunish.",
    skills: ["Do'konlarda xarid qilish", "Yo'l so'rash", "Qisqa hikoyalar o'qish", "Oddiy xatlar yozish"],
  },
  {
    level: "B1",
    title: "Intermediate",
    duration: "4-6 oy",
    icon: "🌳",
    description: "Mustaqil muloqot, murakkabroq matnlar, fikr bildirish.",
    skills: ["Sayohat rejalashtirish", "Ish suhbatlari", "Maqolalar o'qish", "Insho yozish (150 so'z)"],
  },
  {
    level: "B2",
    title: "Upper Intermediate",
    duration: "6-8 oy",
    icon: "🚀",
    description: "Erkin muloqot, professional mavzular, murakkab grammatika.",
    skills: ["Biznes muzokaralar", "Prezentatsiyalar", "Ilmiy matnlar", "Rasmiy xatlar"],
  },
  {
    level: "C1",
    title: "Advanced",
    duration: "8-12 oy",
    icon: "⭐",
    description: "Professional daraja, murakkab tahlillar, akademik yozish.",
    skills: ["Akademik yozish", "Debatlar", "Ilmiy tadqiqot", "IELTS 7.0+"],
  },
  {
    level: "C2",
    title: "Proficiency",
    duration: "12+ oy",
    icon: "👑",
    description: "Mukammal bilish, native speaker darajasi, har qanday mavzu.",
    skills: ["Adabiy tahlil", "Professional tarjima", "Murakkab munozaralar", "IELTS 8.5+"],
  },
];

export function LearningJourney() {
  const [selectedStep, setSelectedStep] = useState<number | null>(null);

  // Modal ochiqligida orqa sahifa scroll bo'lmasin (iOS/Android)
  useEffect(() => {
    if (selectedStep === null) return;
    document.body.classList.add("no-scroll");
    return () => document.body.classList.remove("no-scroll");
  }, [selectedStep]);

  return (
    // ✅ 1. Orqa fon rangi olib tashlandi (transparent)
    <section className="relative py-24 px-6" id="journey">
      <div className="max-w-5xl mx-auto">
        
        {/* Sarlavha */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-block bg-orange-500/20 text-orange-400 text-sm font-semibold px-4 py-2 rounded-full mb-4 border border-orange-500/30">
            O'quv Yo'li
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            A1 dan C2 gacha{" "}
            {/* ✅ 3. Asosiy rang ORANGE ga o'zgartirildi */}
            <span className="bg-gradient-to-r from-orange-500 to-rose-500 bg-clip-text text-transparent">
              transformatsiya
            </span>
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Har bir daraja sizni yangi imkoniyatlarga olib chiqadi
          </p>
        </motion.div>

        {/* Timeline Container */}
        <div className="relative max-w-3xl mx-auto">
          
          {/* Markaziy chiziq (Orange) */}
          <div className="absolute left-4 md:left-1/2 transform md:-translate-x-1/2 w-1 h-full bg-slate-800 rounded-full overflow-hidden">
            <motion.div
              initial={{ height: "0%" }}
              whileInView={{ height: "100%" }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 1.5, ease: "easeInOut" }}
              className="w-full bg-gradient-to-b from-orange-400 via-orange-500 to-rose-500 shadow-[0_0_15px_rgba(249,115,22,0.6)]"
            />
          </div>

          {/* Timeline Steps */}
          <div className="relative space-y-12 md:space-y-16">
            {JOURNEY_STEPS.map((step, idx) => {
              const isLeft = idx % 2 === 0;
              return (
                <motion.div
                  key={step.level}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ delay: idx * 0.1, duration: 0.5 }}
                  // ✅ Mobile uchun hamisha chapda, Desktop uchun almashinadi
                  className={`relative flex items-center ${
                    isLeft ? "md:flex-row" : "md:flex-row-reverse"
                  } flex-row`}
                >
                  {/* Content Card */}
                  <div className={`w-full md:w-5/12 ${isLeft ? "md:pr-12 pl-12 md:pl-0" : "md:pl-12 pl-12"}`}>
                    <motion.div
                      whileHover={{ scale: 1.02, y: -5 }}
                      onClick={() => setSelectedStep(idx)}
                      className="cursor-pointer group bg-slate-900/40 border border-slate-800 rounded-2xl p-5 md:p-6 hover:border-orange-500/50 transition-all duration-300 shadow-lg"
                    >
                      <div className="flex items-center gap-4 mb-3">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-rose-500 flex items-center justify-center text-2xl shadow-lg shadow-orange-500/20">
                          {step.icon}
                        </div>
                        <div>
                          <div className="text-xs text-orange-400 font-semibold">{step.duration}</div>
                          <h3 className="text-lg md:text-xl font-bold text-white">
                            {step.level} - {step.title}
                          </h3>
                        </div>
                      </div>
                      <p className="text-sm text-slate-300 mb-3">{step.description}</p>
                      <div className="text-xs text-orange-400 font-semibold flex items-center gap-1">
                        Batafsil ko'rish
                        <span className="animate-nudge-x inline-block">→</span>
                      </div>
                    </motion.div>
                  </div>

                  {/* Center Dot */}
                  <div className="absolute left-4 md:left-1/2 transform -translate-x-1/2 z-10">
                    <motion.div
                      whileHover={{ scale: 1.3 }}
                      className="w-5 h-5 md:w-6 md:h-6 rounded-full bg-gradient-to-br from-orange-400 to-rose-500 shadow-[0_0_15px_rgba(249,115,22,0.8)] border-4 border-slate-950"
                    />
                  </div>

                  {/* Empty Space for Desktop */}
                  <div className="hidden md:block md:w-5/12" />
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>

      {/* AnimatePresence Modal */}
      <AnimatePresence>
        {selectedStep !== null && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
            onClick={() => setSelectedStep(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              transition={{ type: "spring", duration: 0.4 }}
              onClick={(e) => e.stopPropagation()}
              className="relative bg-slate-900 border border-slate-700 rounded-3xl p-6 md:p-8 max-w-2xl w-full shadow-2xl"
            >
              <button
                onClick={() => setSelectedStep(null)}
                className="absolute top-4 right-4 w-10 h-10 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-white transition-colors"
              >
                ✕
              </button>

              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-orange-500 to-rose-500 flex items-center justify-center text-4xl shadow-lg shadow-orange-500/20">
                  {JOURNEY_STEPS[selectedStep].icon}
                </div>
                <div>
                  <div className="text-sm text-orange-400 font-semibold">
                    {JOURNEY_STEPS[selectedStep].duration}
                  </div>
                  <h2 className="text-2xl md:text-3xl font-bold text-white">
                    {JOURNEY_STEPS[selectedStep].level} - {JOURNEY_STEPS[selectedStep].title}
                  </h2>
                </div>
              </div>

              <p className="text-slate-300 text-lg mb-6">{JOURNEY_STEPS[selectedStep].description}</p>

              <div className="mb-6">
                <h3 className="text-lg font-bold text-white mb-3">Nima o'rganasiz:</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {JOURNEY_STEPS[selectedStep].skills.map((skill: string, idx: number) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="flex items-center gap-2 bg-slate-800/50 rounded-xl p-3 border border-slate-700/50"
                    >
                      <div className="w-2 h-2 rounded-full bg-orange-500" />
                      <span className="text-slate-300 text-sm">{skill}</span>
                    </motion.div>
                  ))}
                </div>
              </div>

              <button
                onClick={() => setSelectedStep(null)}
                className="w-full py-3 bg-gradient-to-r from-orange-500 to-rose-500 text-white font-bold rounded-xl hover:opacity-90 transition-opacity shadow-lg shadow-orange-500/20"
              >
                Tushundim
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}