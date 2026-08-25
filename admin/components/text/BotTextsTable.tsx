'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Save, RotateCcw, Check, X, Trash2 } from 'lucide-react';
import { BotText, getBotTexts, bulkUpsertBotTexts, deleteBotText } from '@/lib/api';

export function BotTextsTable() {
  const [texts, setTexts] = useState<BotText[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterLang, setFilterLang] = useState<string>('all');
  const [editedRows, setEditedRows] = useState<Map<number, string>>(new Map());
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const groupedTexts = texts.reduce<Record<string, BotText[]>>((acc, text) => {
    if (!acc[text.key]) acc[text.key] = [];
    acc[text.key].push(text);
    return acc;
  }, {});

  const loadTexts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getBotTexts();
      setTexts(data);
    } catch (err) {
      showMessage('error', 'Matnlarni yuklashda xatolik');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTexts();
  }, [loadTexts]);

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  };

  const handleEdit = (id: number, newText: string) => {
    setEditedRows(prev => {
      const newMap = new Map(prev);
      newMap.set(id, newText);
      return newMap;
    });
  };

  const handleCancel = (id: number) => {
    setEditedRows(prev => {
      const newMap = new Map(prev);
      newMap.delete(id);
      return newMap;
    });
  };

  const handleSaveAll = async () => {
    if (editedRows.size === 0) {
      showMessage('error', 'Hech qanday ozgarish yoq');
      return;
    }

    setSaving(true);
    try {
      const updates = Array.from(editedRows.entries()).map(([id, text]) => {
        const original = texts.find(t => t.id === id);
        return {
          key: original!.key,
          lang: original!.lang,
          text: text,
        };
      });

      await bulkUpsertBotTexts(updates);
      
      setTexts(prev => prev.map(t => {
        const newText = editedRows.get(t.id);
        return newText !== undefined ? { ...t, text: newText } : t;
      }));

      setEditedRows(new Map());
      showMessage('success', `${updates.length} ta matn muvaffaqiyatli saqlandi`);
    } catch (err) {
      showMessage('error', 'Saqlashda xatolik');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Haqiqatan ham ochirmoqchimisiz?')) return;

    try {
      await deleteBotText(id);
      setTexts(prev => prev.filter(t => t.id !== id));
      editedRows.delete(id);
      showMessage('success', 'Matn ochirildi');
    } catch (err) {
      showMessage('error', 'Ochirishda xatolik');
    }
  };

  const filteredKeys = Object.keys(groupedTexts).filter(key => {
    if (searchQuery && !key.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (filterLang !== 'all') {
      return groupedTexts[key].some(t => t.lang === filterLang);
    }
    return true;
  });

  const hasChanges = editedRows.size > 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {message && (
        <div className={`p-4 rounded-lg ${
          message.type === 'success' 
            ? 'bg-green-500/20 border border-green-500 text-green-200' 
            : 'bg-red-500/20 border border-red-500 text-red-200'
        }`}>
          {message.text}
        </div>
      )}

      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" size={20} />
            <input
              type="text"
              placeholder="Kalit boyicha qidirish..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-dark-800 border border-dark-700 rounded-lg pl-10 pr-4 py-2 text-white placeholder-stone-500 focus:outline-none focus:border-primary-500"
            />
          </div>
          <select
            value={filterLang}
            onChange={(e) => setFilterLang(e.target.value)}
            className="bg-dark-800 border border-dark-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-500"
          >
            <option value="all">Barcha tillar</option>
            <option value="uz">Ozbek</option>
            <option value="ru">Russkiy</option>
            <option value="en">English</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => handleSaveAll()}
            disabled={!hasChanges || saving}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              hasChanges
                ? 'bg-primary-600 hover:bg-primary-700 text-white'
                : 'bg-dark-700 text-stone-500 cursor-not-allowed'
            }`}
          >
            <Save size={18} />
            {saving ? 'Saqlanmoqda...' : `Saqlash (${editedRows.size})`}
          </button>
          <button
            onClick={loadTexts}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-800 hover:bg-dark-700 text-white transition-colors"
          >
            <RotateCcw size={18} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-dark-800 rounded-lg p-4 border border-dark-700">
          <p className="text-stone-400 text-sm">Jami matnlar</p>
          <p className="text-2xl font-bold text-white">{texts.length}</p>
        </div>
        <div className="bg-dark-800 rounded-lg p-4 border border-dark-700">
          <p className="text-stone-400 text-sm">Noyob kalitlar</p>
          <p className="text-2xl font-bold text-white">{Object.keys(groupedTexts).length}</p>
        </div>
        <div className="bg-dark-800 rounded-lg p-4 border border-dark-700">
          <p className="text-stone-400 text-sm">Ozgarishlar</p>
          <p className={`text-2xl font-bold ${hasChanges ? 'text-yellow-400' : 'text-white'}`}>
            {editedRows.size}
          </p>
        </div>
      </div>

      <div className="bg-dark-800 rounded-lg border border-dark-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-dark-900 border-b border-dark-700">
            <tr>
              <th className="text-left px-6 py-3 text-stone-400 text-sm font-medium">Kalit</th>
              <th className="text-left px-6 py-3 text-stone-400 text-sm font-medium">Ozbek</th>
              <th className="text-left px-6 py-3 text-stone-400 text-sm font-medium">Russkiy</th>
              <th className="text-left px-6 py-3 text-stone-400 text-sm font-medium">English</th>
              <th className="text-right px-6 py-3 text-stone-400 text-sm font-medium">Amallar</th>
            </tr>
          </thead>
          <tbody>
            {filteredKeys.map((key) => {
              const uz = groupedTexts[key].find(t => t.lang === 'uz');
              const ru = groupedTexts[key].find(t => t.lang === 'ru');
              const en = groupedTexts[key].find(t => t.lang === 'en');

              return (
                <tr key={key} className="border-b border-dark-700 hover:bg-dark-900/50">
                  <td className="px-6 py-4">
                    <code className="text-primary-400 text-sm bg-dark-900 px-2 py-1 rounded">
                      {key}
                    </code>
                  </td>
                  {([
                    { text: uz, lang: 'uz' },
                    { text: ru, lang: 'ru' },
                    { text: en, lang: 'en' },
                  ] as const).map(({ text, lang }) => (
                    <td key={lang} className="px-6 py-4">
                      {text ? (
                        <EditableCell
                          text={text}
                          onChange={(newVal) => handleEdit(text.id, newVal)}
                          onCancel={() => handleCancel(text.id)}
                          isEdited={editedRows.has(text.id)}
                        />
                      ) : (
                        <span className="text-stone-600 italic">—</span>
                      )}
                    </td>
                  ))}
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      {uz && (
                        <button
                          onClick={() => handleDelete(uz.id)}
                          className="p-2 rounded-lg hover:bg-red-500/20 text-stone-400 hover:text-red-400 transition-colors"
                          title="Ochirish (uz)"
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {filteredKeys.length === 0 && (
        <div className="text-center py-12 text-stone-500">
          Hech narsa topilmadi
        </div>
      )}
    </div>
  );
}

interface EditableCellProps {
  text: BotText;
  onChange: (newVal: string) => void;
  onCancel: () => void;
  isEdited: boolean;
}

function EditableCell({ text, onChange, onCancel, isEdited }: EditableCellProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [localValue, setLocalValue] = useState(text.text);

  const handleSave = () => {
    if (localValue !== text.text) {
      onChange(localValue);
    }
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setLocalValue(text.text);
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="flex items-center gap-2">
        <textarea
          value={localValue}
          onChange={(e) => setLocalValue(e.target.value)}
          autoFocus
          rows={2}
          className="flex-1 bg-dark-900 border border-dark-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500 resize-none"
        />
        <button
          onClick={handleSave}
          className="p-2 rounded-lg bg-green-500/20 hover:bg-green-500/30 text-green-400 transition-colors"
        >
          <Check size={16} />
        </button>
        <button
          onClick={handleCancelEdit}
          className="p-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-400 transition-colors"
        >
          <X size={16} />
        </button>
      </div>
    );
  }

  return (
    <div
      onClick={() => setIsEditing(true)}
      className={`px-3 py-2 rounded cursor-pointer text-sm transition-colors ${
        isEdited
          ? 'bg-yellow-500/10 border border-yellow-500/30 text-yellow-200'
          : 'bg-dark-900 border border-dark-700 text-stone-300 hover:border-dark-600'
      }`}
    >
      {text.text.length > 80 ? text.text.substring(0, 80) + '...' : text.text}
    </div>
  );
}