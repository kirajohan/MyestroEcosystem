"use client";

import { motion } from "framer-motion";

interface Criterion {
  name: string;
  score: number;
  max_score: number;
  comment: string;
}

interface Correction {
  original: string;
  corrected: string;
  explanation: string;
}

interface WritingFeedback {
  overall_score: number;
  cefr_estimate?: string;
  criteria?: Criterion[];
  corrections?: Correction[];
  strengths?: string[];
  weaknesses?: string[];
  recommendations?: string[];
  error?: string;
}

interface WritingResultProps {
  feedback: WritingFeedback;
}

export default function WritingResult({ feedback }: WritingResultProps) {
  if (feedback.error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
        ❌ AI baholashda xato: {feedback.error}
      </div>
    );
  }

  const scoreColor =
    feedback.overall_score >= 70
      ? "text-emerald-600"
      : feedback.overall_score >= 50
      ? "text-amber-600"
      : "text-red-600";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Overall Score */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 text-center">
        <div className="text-xs uppercase tracking-widest text-slate-400 font-semibold mb-2">
          Overall Score
        </div>
        <div className={`text-5xl font-bold ${scoreColor}`}>
          {feedback.overall_score}
          <span className="text-2xl text-slate-400">/100</span>
        </div>
        {feedback.cefr_estimate && (
          <div className="mt-2 inline-block px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-bold">
            Estimated Level: {feedback.cefr_estimate}
          </div>
        )}
      </div>

      {/* Criteria */}
      {feedback.criteria && feedback.criteria.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-bold text-slate-900 mb-4">📊 Criteria Breakdown</h3>
          <div className="space-y-3">
            {feedback.criteria.map((c, idx) => (
              <div key={idx}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium text-slate-700">{c.name}</span>
                  <span className="font-bold text-slate-900">
                    {c.score}/{c.max_score}
                  </span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-orange-500 to-rose-500 rounded-full"
                    style={{ width: `${(c.score / c.max_score) * 100}%` }}
                  />
                </div>
                {c.comment && (
                  <p className="text-xs text-slate-500 mt-1">{c.comment}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Corrections */}
      {feedback.corrections && feedback.corrections.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="font-bold text-slate-900 mb-4">✏️ Corrections</h3>
          <div className="space-y-3">
            {feedback.corrections.map((c, idx) => (
              <div key={idx} className="bg-slate-50 rounded-lg p-3 text-sm">
                <div className="line-through text-red-400 mb-1">{c.original}</div>
                <div className="text-emerald-700 font-medium mb-1">{c.corrected}</div>
                <div className="text-slate-500 text-xs">{c.explanation}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {feedback.strengths && feedback.strengths.length > 0 && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
            <h3 className="font-bold text-emerald-800 mb-2 text-sm">💪 Strengths</h3>
            <ul className="space-y-1">
              {feedback.strengths.map((s, i) => (
                <li key={i} className="text-sm text-emerald-700 flex items-start gap-2">
                  <span>•</span> {s}
                </li>
              ))}
            </ul>
          </div>
        )}

        {feedback.weaknesses && feedback.weaknesses.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <h3 className="font-bold text-amber-800 mb-2 text-sm">⚠️ Areas to Improve</h3>
            <ul className="space-y-1">
              {feedback.weaknesses.map((w, i) => (
                <li key={i} className="text-sm text-amber-700 flex items-start gap-2">
                  <span>•</span> {w}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Recommendations */}
      {feedback.recommendations && feedback.recommendations.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <h3 className="font-bold text-blue-800 mb-2 text-sm">💡 Recommendations</h3>
          <ul className="space-y-1">
            {feedback.recommendations.map((r, i) => (
              <li key={i} className="text-sm text-blue-700 flex items-start gap-2">
                <span>→</span> {r}
              </li>
            ))}
          </ul>
        </div>
      )}
    </motion.div>
  );
}