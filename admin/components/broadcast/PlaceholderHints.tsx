// components/broadcast/PlaceholderHints.tsx
"use client";

import { useState, useEffect } from "react";

interface Placeholder {
  key: string;
  label: string;
  example: string;
}

export default function PlaceholderHints() {
  const [placeholders, setPlaceholders] = useState<Placeholder[]>([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPlaceholders() {
      try {
        const res = await fetch("/api/broadcast/placeholders");
        if (res.ok) {
          const data = await res.json();
          setPlaceholders(data.placeholders || []);
        }
      } catch (e) {
        console.error("Failed to fetch placeholders:", e);
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
      // Fallback for older browsers
      const textarea = document.createElement("textarea");
      textarea.value = key;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      setCopied(key);
      setTimeout(() => setCopied(null), 1500);
    }
  };

  if (loading) return null;

  if (placeholders.length === 0) return null;

  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-3">
      <div className="mb-1.5 text-xs font-medium text-gray-500">
        Shaxsiylashtirish kalit so&#39;zlari
      </div>
      <div className="flex flex-wrap gap-1.5">
        {placeholders.map((p) => (
          <button
            key={p.key}
            onClick={() => copyToClipboard(p.key)}
            className="group relative rounded border border-gray-300 bg-white px-2 py-1 text-xs text-gray-700 hover:border-primary hover:bg-dark-100 hover:text-primary"
            title={`${p.label}: ${p.example}`}
          >
            <code className="text-xs">{p.key}</code>
            {copied === p.key && (
              <span className="absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap rounded bg-gray-800 px-1.5 py-0.5 text-[10px] text-white">
                Nusxalandi
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}