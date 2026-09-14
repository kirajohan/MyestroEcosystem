'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Copy, CheckCircle2, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';

interface Placeholder {
  key: string;
  label: string;
  description: string;
  example: string;
}

interface PlaceholderHintsProps {
  onInsert?: (placeholder: string) => void;
}

export default function PlaceholderHints({ onInsert }: PlaceholderHintsProps) {
  const [placeholders, setPlaceholders] = useState<Placeholder[]>([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    async function fetchPlaceholders() {
      try {
        const res = await fetch('/api/broadcast/placeholders');
        if (res.ok) {
          const data = await res.json();
          setPlaceholders(data.placeholders || []);
        }
      } catch (e) {
        console.error('Failed to fetch placeholders:', e);
      } finally {
        setLoading(false);
      }
    }
    fetchPlaceholders();
  }, []);

  const copyToClipboard = async (key: string) => {
    try {
      await navigator.clipboard.writeText(key);
      setCopied(key);
      setTimeout(() => setCopied(null), 1500);
    } catch {
      const textarea = document.createElement('textarea');
      textarea.value = key;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(key);
      setTimeout(() => setCopied(null), 1500);
    }
  };

  const handleClick = (placeholder: Placeholder) => {
    if (onInsert) {
      onInsert(placeholder.key);
      setCopied(placeholder.key);
      setTimeout(() => setCopied(null), 1500);
    } else {
      copyToClipboard(placeholder.key);
    }
  };

  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-8 bg-slate-100 rounded-lg animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (placeholders.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-xs text-slate-500">
          Placeholderlar topilmadi
        </p>
      </div>
    );
  }

  const visiblePlaceholders = isExpanded
    ? placeholders
    : placeholders.slice(0, 5);
  const hasMore = placeholders.length > 5;

  return (
    <div className="space-y-3">
      {/* Intro */}
      <p className="text-xs text-slate-600 leading-relaxed">
        Har bir foydalanuvchi uchun bu kalit sozlar avtomatik ularning
        malumotlari bilan almashtiriladi.
      </p>

      {/* Placeholders List */}
      <div className="space-y-1.5">
        {visiblePlaceholders.map((p) => {
          const isCopied = copied === p.key;
          return (
            <motion.button
              key={p.key}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleClick(p)}
              className="group relative flex items-center gap-3 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-left hover:border-orange-300 hover:bg-orange-50 transition-all"
            >
              {/* Key Badge */}
              <div className="flex-shrink-0 px-2.5 py-1 bg-white border border-slate-200 rounded-lg group-hover:border-orange-300 transition-colors">
                <code className="text-xs font-mono font-bold text-orange-600">
                  {p.key}
                </code>
              </div>

              {/* Label + Example */}
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-900">
                  {p.label}
                </p>
                <p className="text-[10px] text-slate-500 truncate">
                  Masalan: {p.example}
                </p>
              </div>

              {/* Copy Icon */}
              <div className="flex-shrink-0">
                {isCopied ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="flex items-center gap-1 px-2 py-1 bg-emerald-100 rounded-lg"
                  >
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    <span className="text-[10px] font-semibold text-emerald-700">
                      {onInsert ? 'Qoshildi' : 'Nusxalandi'}
                    </span>
                  </motion.div>
                ) : (
                  <div className="w-7 h-7 flex items-center justify-center rounded-lg bg-white border border-slate-200 group-hover:border-orange-300 group-hover:bg-orange-100 transition-colors">
                    <Copy className="w-3.5 h-3.5 text-slate-500 group-hover:text-orange-600 transition-colors" />
                  </div>
                )}
              </div>
            </motion.button>
          );
        })}
      </div>

      {/* Show More / Less */}
      {hasMore && (
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-center gap-1.5 py-2 text-xs font-medium text-orange-600 hover:text-orange-700 bg-orange-50 hover:bg-orange-100 rounded-xl transition-all"
        >
          {isExpanded ? (
            <>
              <ChevronUp className="w-3.5 h-3.5" />
              Kamaytirish
            </>
          ) : (
            <>
              <ChevronDown className="w-3.5 h-3.5" />
              Yana {placeholders.length - 5} ta korsatish
            </>
          )}
        </button>
      )}

      {/* Footer Info */}
      <div className="pt-2 border-t border-slate-100">
        <p className="text-[10px] text-slate-500 flex items-center gap-1.5">
          <Sparkles className="w-3 h-3 text-orange-500" />
          <span>
            {onInsert
              ? 'Bosing — matnga avtomatik qoshiladi'
              : 'Bosing — clipboardga nusxalanadi'}
          </span>
        </p>
      </div>
    </div>
  );
}