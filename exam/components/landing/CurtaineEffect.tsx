"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";

export default function CurtainEffect() {
  const [open, setOpen] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setOpen(false), 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-[100] pointer-events-none">
          {/* Top curtain */}
          <motion.div
            className="absolute top-0 left-0 right-0 h-1/2 bg-gradient-to-br from-orange-600 via-rose-500 to-orange-600"
            initial={{ y: 0 }}
            animate={{ y: "-100%" }}
            exit={{ y: "-100%" }}
            transition={{ duration: 1.1, ease: [0.76, 0, 0.24, 1], delay: 0.3 }}
          />
          {/* Bottom curtain */}
          <motion.div
            className="absolute bottom-0 left-0 right-0 h-1/2 bg-gradient-to-br from-orange-600 via-rose-500 to-orange-600"
            initial={{ y: 0 }}
            animate={{ y: "100%" }}
            exit={{ y: "100%" }}
            transition={{ duration: 1.1, ease: [0.76, 0, 0.24, 1], delay: 0.3 }}
          />
          {/* Logo in the middle */}
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            initial={{ opacity: 1, scale: 1 }}
            animate={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            <div className="text-center">
              <div className="text-6xl font-bold text-white mb-2 tracking-tight">
                Maestro
              </div>
              <div className="text-sm text-white/80 tracking-[0.3em] uppercase">
                Exam
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}