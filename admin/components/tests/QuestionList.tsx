// admin/components/tests/QuestionList.tsx
'use client';

import { Pencil, Trash2, CheckCircle2, Lightbulb } from 'lucide-react';
import { TestQuestion } from '@/types/test';

interface QuestionListProps {
  questions: TestQuestion[];
  onEdit: (question: TestQuestion) => void;
  onDelete: (id: number) => void;
}

export default function QuestionList({ questions, onEdit, onDelete }: QuestionListProps) {
  return (
    <div className="divide-y divide-gray-100">
      {questions.map((question, index) => (
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
                {question.options.map((option, optIdx) => (
                  <span
                    key={optIdx}
                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium ${
                      optIdx === question.correct_option_index
                        ? 'bg-green-100 text-green-800 border border-green-200'
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {optIdx === question.correct_option_index && (
                      <CheckCircle2 size={12} className="text-green-600" />
                    )}
                    {option}
                  </span>
                ))}
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
      ))}
    </div>
  );
}