"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTheme } from "@/app/providers";

interface FAQItemProps {
  q: string;
  a: string;
  highlight?: string;
}



function FAQItem({ q, a, highlight }: FAQItemProps) {
  const [open, setOpen] = useState(false);
  const { theme } = useTheme();
  const isDark = theme === "dark";

  return (
    <motion.div
      className={`border rounded-xl mb-3 overflow-hidden transition-all duration-300 ${
        open
          ? isDark
            ? "border-orange-500/50 bg-slate-900/50"
            : "border-orange-500/50 bg-orange-50/50"
          : isDark
          ? "border-slate-800 bg-slate-900/30"
          : "border-slate-200 bg-white"
      }`}
      layout
    >
      <button
        onClick={() => setOpen(!open)}
        className="w-full p-5 flex items-center justify-between text-left gap-4"
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
            <div className="px-5 pb-5 space-y-3">
              <p
                className={`leading-relaxed ${
                  isDark ? "text-slate-400" : "text-slate-600"
                }`}
              >
                {a}
              </p>
              
              {/* Highlight/Blockquote */}
              {highlight && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 }}
                  className={`border-l-4 pl-4 py-2 rounded-r-lg ${
                    isDark
                      ? "border-orange-500 bg-orange-500/10"
                      : "border-orange-500 bg-orange-50"
                  }`}
                >
                  <p
                    className={`text-sm font-medium ${
                      isDark ? "text-orange-300" : "text-orange-700"
                    }`}
                  >
                    {highlight}
                  </p>
                </motion.div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

interface FAQProps {
  items: { q: string; a: string; highlight?: string }[];
}

export default function FAQ({ items }: FAQProps) {
  const { theme } = useTheme();
  const isDark = theme === "dark";

  return (
    <section id="faq" className="max-w-3xl mx-auto px-6 py-24">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="text-center mb-12"
      >
        <div className="inline-block bg-orange-500/20 text-orange-400 text-sm font-semibold px-4 py-2 rounded-full mb-4 border border-orange-500/30">
          FAQ
        </div>
        <h2
          className={`text-4xl md:text-5xl font-bold ${
            isDark ? "text-white" : "text-slate-900"
          }`}
        >
          Ko'p so'raladigan{" "}
          <span className="bg-gradient-to-r from-orange-500 to-rose-500 bg-clip-text text-transparent">
            savollar
          </span>
        </h2>
      </motion.div>
      
      <div className="space-y-3">
        {items.map((item, idx) => (
          <motion.div
            key={item.q}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: idx * 0.05 }}
          >
            <FAQItem q={item.q} a={item.a} highlight={item.highlight} />
          </motion.div>
        ))}
      </div>
      
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="text-center mt-12"
      >
        <p className={`text-sm ${isDark ? "text-slate-400" : "text-slate-600"}`}>
          Boshqa savollaringiz bormi?{" "}
          <a
            href="https://t.me/myestro_support"
            className="text-orange-500 hover:text-orange-600 font-semibold transition-colors"
          >
            Biz bilan bog'laning →
          </a>
        </p>
      </motion.div>
    </section>
  );
}