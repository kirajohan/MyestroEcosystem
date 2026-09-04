"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const DEMO_TABS = [
  { id: "ielts", label: "IELTS", color: "from-red-500 to-orange-500" },
  { id: "cefr", label: "CEFR", color: "from-blue-600 to-indigo-600" },
  { id: "toefl", label: "TOEFL", color: "from-green-500 to-emerald-600" },
];

export function InteractiveDemoSection() {
  const [activeTab, setActiveTab] = useState("ielts");
  const [writingText, setWritingText] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showWritingResult, setShowWritingResult] = useState(false);
  
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);

  // Yozib olish taymeri
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } else {
      setRecordingTime(0);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const handleAnalyze = () => {
    if (!writingText.trim()) return;
    setIsAnalyzing(true);
    setShowWritingResult(false);
    
    // AI tahlilini simulyatsiya qilish (2.5 soniya)
    setTimeout(() => {
      setIsAnalyzing(false);
      setShowWritingResult(true);
    }, 2500);
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
  };

  return (
<section className="relative py-24 overflow-hidden">
  {/* Gradient fon - boshqa bo'limlar bilan silliq o'tish */}
    <div className="absolute inset-0 bg-gradient-to-b from-slate-900 via-slate-950/80 to-slate-900 backdrop-blur-xl" />
    
    {/* Neon glow effektlari */}
    <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
    <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
    
    {/* Kontent */}
    <div className="relative max-w-6xl mx-auto px-6">

      <div className="relative max-w-6xl mx-auto px-6">
        {/* Sarlavha */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <div className="inline-block bg-orange-500/20 text-orange-400 text-sm font-semibold px-4 py-2 rounded-full mb-4 border border-orange-500/30">
            Sinab ko`ring
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Interaktiv{" "}
            <span className="bg-gradient-to-r from-orange-500 to-amber-400 bg-clip-text text-transparent">
              o`rganish
            </span>
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Sun`iy intellekt yordamida yozishingiz va gapirishingizni real vaqtda tekshiring.
          </p>
        </motion.div>

        {/* Exam Format Tabs */}
        <div className="flex justify-center mb-10">
          <div className="bg-slate-900/50 backdrop-blur-md p-1.5 rounded-2xl border border-slate-800 inline-flex">
            {DEMO_TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
                  activeTab === tab.id ? "text-white" : "text-slate-400 hover:text-white"
                }`}
              >
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="activeTab"
                    className={`absolute inset-0 bg-gradient-to-r ${tab.color} rounded-xl shadow-lg`}
                    transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                  />
                )}
                <span className="relative z-10">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Demo Grid: 2 ta asosiy karta */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* 1. AI Writing & Grammar Checker */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="relative group"
          >
            {/* Glassmorphism & Dark Glow Border */}
            <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-3xl blur opacity-20 group-hover:opacity-50 transition duration-500" />
            <div className="relative bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-3xl p-6 h-full flex flex-col">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-xl shadow-lg">
                  ✍️
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">AI Writing Checker</h3>
                  <p className="text-xs text-slate-400">Grammatika va uslubni tekshirish</p>
                </div>
              </div>

              <div className="relative flex-1 flex flex-col">
                <textarea
                  value={writingText}
                  onChange={(e) => setWritingText(e.target.value)}
                  placeholder="Ingliz tilida qisqa matn yozing (masalan: I has went to school yesterday)..."
                  className="w-full flex-1 bg-slate-950/50 border border-slate-800 rounded-xl p-4 text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 resize-none transition-all min-h-[160px]"
                />
                
                {/* ⚡ Laser Scanning Effect */}
                <AnimatePresence>
                  {isAnalyzing && (
                    <motion.div
                      initial={{ top: 0, opacity: 0 }}
                      animate={{ top: "100%", opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 2, ease: "linear" }}
                      className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_20px_rgba(34,211,238,0.8)] z-20 pointer-events-none rounded-full"
                    />
                  )}
                </AnimatePresence>

                <button
                  onClick={handleAnalyze}
                  disabled={!writingText.trim() || isAnalyzing}
                  className="mt-4 w-full py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.97] flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20"
                >
                  {isAnalyzing ? (
                    <>
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                      />
                      Tahlil qilinmoqda...
                    </>
                  ) : (
                    <>🚀 Tekshirish</>
                  )}
                </button>
              </div>

              {/* 📊 Animated Progress Meters & Results */}
              <AnimatePresence>
                {showWritingResult && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-6 pt-6 border-t border-slate-800 overflow-hidden"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-slate-400 text-sm font-medium">Umumiy Ball</span>
                      <span className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
                        7.0
                      </span>
                    </div>
                    
                    <div className="space-y-3 mb-4">
                      <ProgressMeter label="Grammar" score={75} color="bg-emerald-500" />
                      <ProgressMeter label="Vocabulary" score={82} color="bg-blue-500" />
                      <ProgressMeter label="Coherence" score={68} color="bg-amber-500" />
                    </div>

                    <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                      <p className="text-sm text-red-300">
                        <span className="font-semibold">Xato:</span>{" "}
                        <span className="line-through opacity-70">I has went</span>{" "}
                        <span className="text-emerald-400 font-semibold">➔ I went</span>
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>

          {/* 2. AI Voice & Pronunciation Visualizer */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="relative group"
          >
            <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl blur opacity-20 group-hover:opacity-50 transition duration-500" />
            <div className="relative bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-3xl p-6 h-full flex flex-col">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center text-xl shadow-lg">
                  🎤
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Speaking Visualizer</h3>
                  <p className="text-xs text-slate-400">Talaffuz va ravonlikni baholash</p>
                </div>
                {isRecording && (
                  <span className="ml-auto flex items-center gap-1.5 text-xs font-semibold text-red-400 bg-red-500/10 px-2 py-1 rounded-full border border-red-500/20">
                    <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                    REC {recordingTime}s
                  </span>
                )}
              </div>

              <div className="flex-1 flex flex-col items-center justify-center min-h-[200px] bg-slate-950/50 rounded-2xl border border-slate-800/50 relative overflow-hidden">
                {/* 🎵 Dynamic Soundwave Animation */}
                <div className="flex items-center gap-1.5 h-16">
                  {Array.from({ length: 24 }).map((_, i) => (
                    <motion.div
                      key={i}
                      animate={
                        isRecording
                          ? { height: [8, 40 + Math.random() * 24, 8] }
                          : { height: 4 }
                      }
                      transition={
                        isRecording
                          ? {
                              duration: 0.4,
                              repeat: Infinity,
                              ease: "easeInOut",
                              delay: i * 0.04,
                            }
                          : { duration: 0.3 }
                      }
                      className={`w-1.5 rounded-full ${
                        isRecording
                          ? "bg-gradient-to-t from-purple-500 to-pink-500 shadow-[0_0_10px_rgba(236,72,153,0.5)]"
                          : "bg-slate-700"
                      }`}
                    />
                  ))}
                </div>

                <p className="mt-6 text-slate-400 text-sm text-center px-4">
                  {isRecording
                    ? "Gapirishni davom eting... AI tinglamoqda."
                    : "Mikrofon tugmasini bosib, 60 soniya davomida ingliz tilida gapiring."}
                </p>
              </div>

              <button
                onClick={toggleRecording}
                className={`mt-6 w-full py-3 font-semibold rounded-xl transition-all duration-300 active:scale-[0.97] flex items-center justify-center gap-2 shadow-lg ${
                  isRecording
                    ? "bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500/30 shadow-red-500/10"
                    : "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white shadow-purple-500/20"
                }`}
              >
                {isRecording ? (
                  <>⏹ To`xtatish</>
                ) : (
                  <>🎙 Yozib olishni boshlash</>
                )}
              </button>

              {/* Speaking Result Simulation */}
              <AnimatePresence>
                {!isRecording && recordingTime > 3 && (
                   <motion.div
                   initial={{ opacity: 0, y: 10 }}
                   animate={{ opacity: 1, y: 0 }}
                   className="mt-4 p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg"
                 >
                   <p className="text-sm text-purple-300 flex items-center gap-2">
                     <span className="text-lg">✨</span>
                     <span>AI tahlili: Fluency 85%, Pronunciation 78%. Ajoyib natija!</span>
                   </p>
                 </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>

        </div>
      </div>
      </div>
    </section>
  );
}

// 📊 Helper Component: Animated Progress Meter
function ProgressMeter({ label, score, color }: { label: string; score: number; color: string }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1.5">
        <span className="text-slate-300 font-medium">{label}</span>
        <span className="text-slate-400">{score}%</span>
      </div>
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          className={`h-full rounded-full ${color} shadow-[0_0_10px_currentColor]`}
        />
      </div>
    </div>
  );
}