'use client';

import { Pencil, Trash2, CheckCircle2, Lightbulb } from 'lucide-react';
import { TestQuestion } from '@/types/test';

interface QuestionListProps {
  questions: TestQuestion[];
  onEdit: (question: TestQuestion) => void;
  onDelete: (id: number) => void;
}

export default function QuestionList({ questions, onEdit, onDelete }: QuestionListProps) {
  // ✅ Helper: options formatini tekshirish
  const getOptionText = (option: any): string => {
    if (typeof option === 'string') return option;
    if (typeof option === 'object' && option !== null) {
      return option.text || option.label || String(option);
    }
    return String(option);
  };

  // ✅ Helper: to'g'ri javob indeksini topish
  const getCorrectIndex = (question: TestQuestion): number => {
    // Agar correct_option_index mavjud bo'lsa
    if (question.correct_option_index !== undefined && question.correct_option_index !== null) {
      return question.correct_option_index;
    }
    
    // Agar correct_answer mavjud bo'lsa (import qilingan testlar uchun)
    if (question.correct_answer) {
      const label = question.correct_answer; // "A", "B", "C"
      return label.charCodeAt(0) - 'A'.charCodeAt(0);
    }
    
    // Agar options ichida is_correct bo'lsa
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

  return (
    <div className="divide-y divide-gray-100">
      {questions.map((question, index) => {
        const correctIdx = getCorrectIndex(question);
        
        return (
          <div key={question.id} className="p-5 hover:bg-gray-50/50 transition-colors">
            <div className="flex items-start justify-between gap-4">
              {/* Question Content */}
              <div className="flex-1 min-w-0">
                {/* Question Number + Text */}
                <div className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-700 text-xs font-bold rounded-full flex items-center justify-center mt-0.5">
                    {index + 1}
                  </span>
                  <p className="text-sm font-medium text-gray-900 leading-relaxed">
                    {question.question_text}
                  </p>
                </div>

                {/* Options */}
                <div className="mt-3 ml-8 flex flex-wrap gap-2">
                  {question.options.map((option, optIdx) => {
                    const optionText = getOptionText(option);
                    const isCorrect = optIdx === correctIdx;
                    
                    return (
                      <span
                        key={optIdx}
                        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium ${
                          isCorrect
                            ? 'bg-green-100 text-green-800 border border-green-200'
                            : 'bg-gray-100 text-gray-600'
                        }`}
                      >
                        {isCorrect && <CheckCircle2 size={12} className="text-green-600" />}
                        {optionText}
                      </span>
                    );
                  })}
                </div>

                {/* Explanation */}
                {question.explanation && (
                  <div className="mt-2 ml-8 flex items-start gap-1.5">
                    <Lightbulb size={12} className="text-amber-500 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-gray-500 italic">{question.explanation}</p>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-1 flex-shrink-0">
                <button
                  onClick={() => onEdit(question)}
                  className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="Tahrirlash"
                >
                  <Pencil size={15} />
                </button>
                <button
                  onClick={() => onDelete(question.id)}
                  className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  title="O'chirish"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}