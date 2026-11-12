'use client';

import { Pencil, Trash2, CheckCircle2, Lightbulb, FileQuestion } from 'lucide-react';
import { motion } from 'framer-motion';
import { TestQuestion } from '@/types/test';

interface QuestionListProps {
  questions: TestQuestion[];
  onEdit: (question: TestQuestion) => void;
  onDelete: (id: number) => void;
}

export default function QuestionList({ questions, onEdit, onDelete }: QuestionListProps) {
  const getOptionText = (option: any): string => {
    if (typeof option === 'string') return option;
    if (typeof option === 'object' && option !== null) {
      return option.text || option.label || String(option);
    }
    return String(option);
  };

  const getCorrectIndex = (question: TestQuestion): number => {
    if (question.correct_option_index !== undefined && question.correct_option_index !== null) {
      return question.correct_option_index;
    }

    if (question.correct_answer) {
      const label = question.correct_answer;
      return label.charCodeAt(0) - 65; // 'A'.charCodeAt(0) = 65
    }

    if (Array.isArray(question.options) && question.options.length > 0) {
      const correctIdx = question.options.findIndex((opt: any) => {
        if (typeof opt === 'object' && opt !== null) {
          return opt.is_correct === true;
        }
        return false;
      });
      if (correctIdx !== -1) return correctIdx;
    }

    return 0;
  };

  if (questions.length === 0) {
    return (
      <div className="p-12 text-center">
        <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <FileQuestion className="w-8 h-8 text-slate-300" />
        </div>
        <h3 className="text-base font-semibold text-slate-900 mb-1">Savollar mavjud emas</h3>
        <p className="text-sm text-slate-500">Birinchi savolni qoshish orqali testni toldiring</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-slate-100">
      {questions.map((question, index) => {
        const correctIdx = getCorrectIndex(question);

        return (
          <motion.div
            key={question.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.03 }}
            className="p-5 hover:bg-slate-50/50 transition-colors group"
          >
            <div className="flex flex-col sm:flex-row items-start justify-between gap-3 sm:gap-4">
              {/* Question Content */}
              <div className="flex-1 min-w-0">
                {/* Question Number + Text */}
                <div className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-7 h-7 bg-gradient-to-br from-orange-500 to-orange-600 text-white text-xs font-bold rounded-lg flex items-center justify-center mt-0.5 shadow-sm shadow-orange-500/20">
                    {index + 1}
                  </span>
                  <p className="text-sm font-medium text-slate-900 leading-relaxed flex-1">
                    {question.question_text}
                  </p>
                </div>

                {/* Options */}
                <div className="mt-3 ml-0 sm:ml-10 flex flex-wrap gap-2">
                  {question.options.map((option, optIdx) => {
                    const optionText = getOptionText(option);
                    const isCorrect = optIdx === correctIdx;
                    const letter = String.fromCharCode(65 + optIdx);

                    return (
                      <span
                        key={optIdx}
                        className={`inline-flex max-w-full min-w-0 items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium break-words transition-colors ${
                          isCorrect
                            ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                            : 'bg-slate-50 text-slate-600 border border-slate-200'
                        }`}
                      >
                        <span
                          className={`w-4 h-4 rounded text-[10px] font-bold flex items-center justify-center ${
                            isCorrect ? 'bg-emerald-500 text-white' : 'bg-slate-200 text-slate-600'
                          }`}
                        >
                          {letter}
                        </span>
                        {isCorrect && <CheckCircle2 size={12} className="text-emerald-600" />}
                        {optionText}
                      </span>
                    );
                  })}
                </div>

                {/* Explanation */}
                {question.explanation && (
                  <div className="mt-3 ml-0 sm:ml-10 flex items-start gap-2 p-3 bg-amber-50 border border-amber-100 rounded-lg">
                    <Lightbulb size={14} className="text-amber-500 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-amber-800 italic leading-relaxed">
                      {question.explanation}
                    </p>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-1 flex-shrink-0 opacity-60 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => onEdit(question)}
                  className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="Tahrirlash"
                >
                  <Pencil size={15} />
                </button>
                <button
                  onClick={() => onDelete(question.id)}
                  className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  title="Ochirish"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}