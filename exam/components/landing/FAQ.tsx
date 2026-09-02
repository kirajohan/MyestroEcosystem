"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTheme } from "@/app/providers";

interface FAQItemProps {
  q: string;
  a: string;
}

function FAQItem({ q, a }: FAQItemProps) {
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

interface FAQProps {
  items: { q: string; a: string }[];
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
        <h2
          className={`text-4xl md:text-5xl font-bold ${
            isDark ? "text-white" : "text-slate-900"
          }`}
        >
          Ko'p so'raladigan savollar
        </h2>
      </motion.div>
      <div className="space-y-2">
        {items.map((item) => (
          <FAQItem key={item.q} q={item.q} a={item.a} />
        ))}
      </div>
    </section>
  );
}