'use client';

import { useCallback, useEffect, useState, FormEvent } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft,
  Plus,
  Trash2,
  Pencil,
  Clock,
  FileText,
  Headphones,
  BookOpen,
  PenTool,
  Mic,
  AlertCircle,
  X,
  Upload,
  Save,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import AudioUpload from '@/app/exam/components/AudioUpload';
import { toast } from 'sonner';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://myestroeco-backend-production.up.railway.app';

interface Option {
  id?: number;
  text: string;
  is_correct: boolean;
  order: number;
}

interface Item {
  id: number;
  block_id: number;
  item_type: string;
  title: string;
  instruction?: string;
  question_text?: string;
  min_words?: number;
  max_words?: number;
  preparation_time_sec?: number;
  answer_time_sec?: number;
  max_score: number;
  order: number;
  options: Option[];
}

interface Block {
  id: number;
  exam_id: number;
  block_type: string;
  title: string;
  description?: string;
  instructions?: string;
  passage_text?: string;
  audio_url?: string;
  audio_duration_sec?: number;
  order: number;
  time_limit_sec: number;
}

const BLOCK_TYPES = [
  { value: 'listening', label: 'Listening', icon: Headphones },
  { value: 'reading', label: 'Reading', icon: BookOpen },
  { value: 'writing', label: 'Writing', icon: PenTool },
  { value: 'speaking', label: 'Speaking', icon: Mic },
];

const ITEM_TYPE_LABELS: Record<string, { label: string; icon: any; color: string }> = {
  listening_question: { label: 'Listening', icon: Headphones, color: 'blue' },
  reading_question: { label: 'Reading', icon: BookOpen, color: 'emerald' },
  writing_task: { label: 'Writing', icon: PenTool, color: 'purple' },
  speaking_task: { label: 'Speaking', icon: Mic, color: 'rose' },
};

export default function BlockEditPage() {
  const router = useRouter();
  const params = useParams();
  const examId = Number(params.id);
  const blockId = Number(params.blockId);
  const { token } = useAuth();

  const [block, setBlock] = useState<Block | null>(null);
  const [items, setItems] = useState<Item[]>([]);
  const [selectedItemId, setSelectedItemId] = useState<number | null>(null);
  const [isCreatingItem, setIsCreatingItem] = useState(false);

  const [loading, setLoading] = useState(true);
  const [savingBlock, setSavingBlock] = useState(false);
  const [savingItem, setSavingItem] = useState(false);
  const [error, setError] = useState('');

  // Block form
  const [blockForm, setBlockForm] = useState({
    title: '',
    description: '',
    instructions: '',
    block_type: 'reading',
    passage_text: '',
    audio_url: '',
    order: 1,
    time_limit_sec: 600,
  });

  // Item form
  const [itemForm, setItemForm] = useState({
    item_type: 'reading_question',
    title: '',
    instruction: '',
    question_text: '',
    min_words: 80,
    max_words: 120,
    preparation_time_sec: 30,
    answer_time_sec: 60,
    max_score: 1,
    order: 1,
  });

  const [itemOptions, setItemOptions] = useState<Option[]>([
    { text: '', is_correct: false, order: 1 },
    { text: '', is_correct: false, order: 2 },
    { text: '', is_correct: false, order: 3 },
    { text: '', is_correct: false, order: 4 },
  ]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const headers = { Authorization: `Bearer ${token}` };

      const blocksRes = await fetch(
        `${API_URL}/api/v2/exam/admin/exams/${examId}/blocks`,
        { headers }
      );
      if (!blocksRes.ok) throw new Error(`HTTP ${blocksRes.status}`);

      const blocks = await blocksRes.json();
      const found = blocks.find((b: Block) => b.id === blockId);
      if (!found) {
        setError('Block topilmadi');
        return;
      }

      setBlock(found);
      setBlockForm({
        title: found.title || '',
        description: found.description || '',
        instructions: found.instructions || '',
        block_type: found.block_type || 'reading',
        passage_text: found.passage_text || '',
        audio_url: found.audio_url || '',
        order: found.order || 1,
        time_limit_sec: found.time_limit_sec || 600,
      });

      const itemsRes = await fetch(
        `${API_URL}/api/v2/exam/admin/blocks/${blockId}/items`,
        { headers }
      );
      if (itemsRes.ok) {
        const itemsData = await itemsRes.json();
        setItems(Array.isArray(itemsData) ? itemsData : itemsData.items || []);
      }
    } catch (err) {
      console.error('Yuklash xatosi:', err);
      setError(err instanceof Error ? err.message : 'Malumotlar yuklanmadi');
    } finally {
      setLoading(false);
    }
  }, [token, blockId, examId]);

  useEffect(() => {
    if (token) loadData();
  }, [token, blockId, loadData]);

  function handleBlockChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) {
    const { name, value, type } = e.target;
    setBlockForm((prev) => ({
      ...prev,
      [name]: type === 'number' ? Number(value) : value,
    }));
  }

  function handleBlockAudioUploaded(url: string) {
    setBlockForm((prev) => ({ ...prev, audio_url: url }));
  }

  async function handleSaveBlock(e: FormEvent) {
    e.preventDefault();
    setError('');
    setSavingBlock(true);

    try {
      const res = await fetch(`${API_URL}/api/v2/exam/admin/blocks/${blockId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(blockForm),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      toast.success('Block saqlandi');
      await loadData();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Saqlashda xato');
    } finally {
      setSavingBlock(false);
    }
  }

  function handleItemChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) {
    const { name, value, type } = e.target;
    setItemForm((prev) => ({
      ...prev,
      [name]: type === 'number' ? Number(value) : value,
    }));
  }

  function handleOptionChange(idx: number, field: 'text' | 'is_correct', value: string | boolean) {
    setItemOptions((prev) =>
      prev.map((opt, i) => (i === idx ? { ...opt, [field]: value } : opt))
    );
  }

  function handleAddOption() {
    setItemOptions((prev) => [
      ...prev,
      { text: '', is_correct: false, order: prev.length + 1 },
    ]);
  }

  function handleRemoveOption(idx: number) {
    setItemOptions((prev) => prev.filter((_, i) => i !== idx));
  }

  function handleSelectItem(itemId: number) {
    const item = items.find((i) => i.id === itemId);
    if (!item) return;

    setSelectedItemId(itemId);
    setIsCreatingItem(false);
    setItemForm({
      item_type: item.item_type,
      title: item.title || '',
      instruction: item.instruction || '',
      question_text: item.question_text || '',
      min_words: item.min_words || 80,
      max_words: item.max_words || 120,
      preparation_time_sec: item.preparation_time_sec || 30,
      answer_time_sec: item.answer_time_sec || 60,
      max_score: item.max_score || 1,
      order: item.order || 1,
    });

    if (item.options && item.options.length > 0) {
      setItemOptions(item.options.map((o) => ({ ...o })));
    } else {
      setItemOptions([
        { text: '', is_correct: false, order: 1 },
        { text: '', is_correct: false, order: 2 },
        { text: '', is_correct: false, order: 3 },
        { text: '', is_correct: false, order: 4 },
      ]);
    }
  }

  function handleCreateNewItem() {
    const defaultItemType =
      block?.block_type === 'listening'
        ? 'listening_question'
        : block?.block_type === 'reading'
        ? 'reading_question'
        : block?.block_type === 'writing'
        ? 'writing_task'
        : 'speaking_task';

    setSelectedItemId(null);
    setIsCreatingItem(true);
    setItemForm({
      item_type: defaultItemType,
      title: '',
      instruction: '',
      question_text: '',
      min_words: 80,
      max_words: 120,
      preparation_time_sec: 30,
      answer_time_sec: 60,
      max_score: 1,
      order: items.length + 1,
    });
    setItemOptions([
      { text: '', is_correct: false, order: 1 },
      { text: '', is_correct: false, order: 2 },
      { text: '', is_correct: false, order: 3 },
      { text: '', is_correct: false, order: 4 },
    ]);
  }

  function handleCancelItem() {
    setSelectedItemId(null);
    setIsCreatingItem(false);
  }

  async function handleSaveItem(e: FormEvent) {
    e.preventDefault();
    setSavingItem(true);
    setError('');

    try {
      const isChoiceType =
        itemForm.item_type === 'reading_question' ||
        itemForm.item_type === 'listening_question';

      const correctIds = itemOptions
        .map((opt, idx) => (opt.is_correct ? idx + 1 : null))
        .filter((id) => id !== null);

      const payload: any = {
        item_type: itemForm.item_type,
        title: itemForm.title,
        instruction: itemForm.instruction,
        question_text: itemForm.question_text,
        max_score: itemForm.max_score,
        order: itemForm.order,
      };

      if (itemForm.item_type === 'writing_task') {
        payload.min_words = itemForm.min_words;
        payload.max_words = itemForm.max_words;
      }

      if (itemForm.item_type === 'speaking_task') {
        payload.preparation_time_sec = itemForm.preparation_time_sec;
        payload.answer_time_sec = itemForm.answer_time_sec;
      }

      if (isChoiceType) {
        payload.options = itemOptions.filter((o) => o.text.trim());
        payload.answer_key = { correct_option_ids: correctIds };
      }

      const url = selectedItemId
        ? `${API_URL}/api/v2/exam/admin/items/${selectedItemId}`
        : `${API_URL}/api/v2/exam/admin/blocks/${blockId}/items`;
      const method = selectedItemId ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `HTTP ${res.status}`);
      }

      toast.success(selectedItemId ? 'Savol yangilandi' : 'Savol yaratildi');
      handleCancelItem();
      await loadData();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Saqlashda xato');
    } finally {
      setSavingItem(false);
    }
  }

  async function handleDeleteItem(itemId: number) {
    if (!confirm('Bu savolni ochirishni xohlaysizmi?')) return;

    try {
      const res = await fetch(`${API_URL}/api/v2/exam/admin/items/${itemId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      setItems((prev) => prev.filter((item) => item.id !== itemId));
      if (selectedItemId === itemId) handleCancelItem();
      toast.success('Savol ochirildi');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Ochirishda xato');
    }
  }

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
      </div>
    );
  }

  if (!block) {
    return (
      <div className="p-6 flex flex-col items-center justify-center min-h-[50vh]">
        <AlertCircle className="w-12 h-12 text-red-400 mb-3" />
        <p className="text-slate-600">{error || 'Block topilmadi'}</p>
      </div>
    );
  }

  const showItemEditor = selectedItemId !== null || isCreatingItem;
  const isListening = blockForm.block_type === 'listening';
  const isReading = blockForm.block_type === 'reading';
  const isWritingItem = itemForm.item_type === 'writing_task';
  const isSpeakingItem = itemForm.item_type === 'speaking_task';
  const showOptions =
    itemForm.item_type === 'reading_question' ||
    itemForm.item_type === 'listening_question';

  const currentBlockType = BLOCK_TYPES.find((b) => b.value === blockForm.block_type);
  const BlockIcon = currentBlockType?.icon || FileText;

  return (
    <div className="flex flex-col min-h-screen bg-slate-50">
      {/* Header */}
      <header className="sticky top-0 z-20 bg-white border-b border-slate-200 shadow-sm">
        <div className="px-4 md:px-6 py-4 flex items-center gap-3">
          <button
            onClick={() => router.push(`/exam/exams/${examId}`)}
            className="p-2 text-slate-600 hover:bg-slate-100 rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center shadow-sm shadow-orange-500/20">
              <BlockIcon className="w-5 h-5 text-white" />
            </div>
            <div className="min-w-0">
              <p className="text-xs text-slate-500">Block</p>
              <h1 className="text-lg font-bold text-slate-900 truncate">{block.title}</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex flex-col lg:flex-row">
        {/* Sidebar - Items List */}
        <aside className="w-full lg:w-80 lg:sticky lg:top-[73px] lg:h-[calc(100vh-73px)] bg-white lg:border-r border-slate-200 flex flex-col shrink-0 lg:overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Savollar</h2>
              <p className="text-xs text-slate-500">{items.length} ta</p>
            </div>
            <button
              onClick={handleCreateNewItem}
              className="flex items-center gap-1.5 px-3 py-2 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg font-medium text-xs hover:from-orange-600 hover:to-orange-700 transition-all shadow-sm shadow-orange-500/20"
            >
              <Plus className="w-3.5 h-3.5" />
              Yangi
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {items.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-14 h-14 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-3">
                  <FileText className="w-7 h-7 text-slate-300" />
                </div>
                <p className="text-sm text-slate-500 mb-3">Hali savollar yoq</p>
                <button
                  onClick={handleCreateNewItem}
                  className="inline-flex items-center gap-1.5 px-3 py-2 bg-orange-50 text-orange-700 rounded-lg text-xs font-medium hover:bg-orange-100 transition"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Birinchi savol
                </button>
              </div>
            ) : (
              items.map((item, index) => {
                const itemInfo = ITEM_TYPE_LABELS[item.item_type] || {
                  label: 'Item',
                  icon: FileText,
                  color: 'slate',
                };
                const Icon = itemInfo.icon;
                const isSelected = selectedItemId === item.id;

                return (
                  <motion.button
                    key={item.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.03 }}
                    onClick={() => handleSelectItem(item.id)}
                    className={`w-full text-left p-3 rounded-xl border-2 transition-all ${
                      isSelected
                        ? 'border-orange-500 bg-orange-50 shadow-sm'
                        : 'border-slate-100 bg-slate-50 hover:border-slate-200 hover:bg-white'
                    }`}
                  >
                    <div className="flex items-start gap-2.5">
                      <div
                        className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ${
                          isSelected ? 'bg-orange-500 text-white' : 'bg-white border border-slate-200'
                        }`}
                      >
                        <Icon className={`w-4 h-4 ${isSelected ? 'text-white' : 'text-slate-500'}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5 mb-0.5">
                          <span className="text-[10px] font-mono bg-slate-200 px-1.5 py-0.5 rounded text-slate-600">
                            #{item.order}
                          </span>
                          <span className="text-[10px] text-slate-500">{itemInfo.label}</span>
                        </div>
                        <h3
                          className={`text-sm font-semibold truncate ${
                            isSelected ? 'text-orange-900' : 'text-slate-900'
                          }`}
                        >
                          {item.title || 'Nomsiz savol'}
                        </h3>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteItem(item.id);
                        }}
                        className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition flex-shrink-0"
                        title="Ochirish"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </motion.button>
                );
              })
            )}
          </div>
        </aside>

        {/* Main Editor */}
        <main className="flex-1 p-4 md:p-6 space-y-6 min-w-0">
          {/* Block Settings */}
          <motion.form
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            onSubmit={handleSaveBlock}
            className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
          >
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-4 flex items-center gap-3">
              <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <BlockIcon className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <h2 className="text-base font-bold text-white">Block sozlamalari</h2>
                <p className="text-xs text-white/80">Asosiy malumotlar</p>
              </div>
            </div>

            <div className="p-5 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                    Block turi
                  </label>
                  <select
                    name="block_type"
                    value={blockForm.block_type}
                    onChange={handleBlockChange}
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                  >
                    {BLOCK_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                    Nomi <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    name="title"
                    value={blockForm.title}
                    onChange={handleBlockChange}
                    required
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                  Yoriqnoma (instructions)
                </label>
                <textarea
                  name="instructions"
                  value={blockForm.instructions}
                  onChange={handleBlockChange}
                  rows={2}
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all resize-none"
                />
              </div>

              {isReading && (
                <div>
                  <label className="block text-sm font-semibold text-slate-900 mb-1.5 flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-emerald-600" />
                    Passage (matn)
                  </label>
                  <textarea
                    name="passage_text"
                    value={blockForm.passage_text}
                    onChange={handleBlockChange}
                    rows={6}
                    placeholder="Reading uchun matn..."
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all font-mono resize-y"
                  />
                </div>
              )}

              {isListening && (
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                  <h3 className="text-sm font-semibold text-blue-900 mb-3 flex items-center gap-2">
                    <Headphones className="w-4 h-4" />
                    Audio fayl
                  </h3>
                  <AudioUpload currentUrl={blockForm.audio_url} onUpload={handleBlockAudioUploaded} />
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-900 mb-1.5">Tartib</label>
                  <input
                    type="number"
                    name="order"
                    value={blockForm.order}
                    onChange={handleBlockChange}
                    min={1}
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                    Vaqt (daqiqa)
                  </label>
                  <input
                    type="number"
                    value={Math.floor(blockForm.time_limit_sec / 60)}
                    onChange={(e) =>
                      setBlockForm((prev) => ({
                        ...prev,
                        time_limit_sec: Number(e.target.value) * 60,
                      }))
                    }
                    min={1}
                    className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={savingBlock}
                className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl font-semibold hover:from-orange-600 hover:to-orange-700 disabled:opacity-50 transition-all shadow-lg shadow-orange-500/20"
              >
                {savingBlock ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Saqlanmoqda...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Blockni saqlash
                  </>
                )}
              </button>
            </div>
          </motion.form>

          {/* Item Editor */}
          <AnimatePresence>
            {showItemEditor && (
              <motion.form
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                onSubmit={handleSaveItem}
                className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
              >
                <div className="bg-gradient-to-r from-slate-800 to-slate-900 p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center">
                      <Pencil className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h2 className="text-base font-bold text-white">
                        {selectedItemId ? 'Savolni tahrirlash' : 'Yangi savol'}
                      </h2>
                      <p className="text-xs text-white/70">
                        {selectedItemId ? 'Mavjud savolni ozgartiring' : 'Blockga yangi savol qoshing'}
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleCancelItem}
                    className="p-2 text-white/70 hover:text-white hover:bg-white/10 rounded-lg transition"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="p-5 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                        Savol turi
                      </label>
                      <select
                        name="item_type"
                        value={itemForm.item_type}
                        onChange={handleItemChange}
                        className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                      >
                        <option value="reading_question">Reading Question</option>
                        <option value="listening_question">Listening Question</option>
                        <option value="writing_task">Writing Task</option>
                        <option value="speaking_task">Speaking Task</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                        Sarlavha <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        name="title"
                        value={itemForm.title}
                        onChange={handleItemChange}
                        required
                        placeholder="Masalan: Question 1"
                        className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                      />
                    </div>
                  </div>

                  {/* Writing Task */}
                  {isWritingItem && (
                    <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 space-y-4">
                      <h3 className="text-sm font-semibold text-purple-900 flex items-center gap-2">
                        <PenTool className="w-4 h-4" />
                        Writing Task
                      </h3>
                      <div>
                        <label className="block text-xs font-medium text-purple-800 mb-1.5">
                          Topshiriq matni <span className="text-red-500">*</span>
                        </label>
                        <textarea
                          name="question_text"
                          value={itemForm.question_text}
                          onChange={handleItemChange}
                          required
                          rows={4}
                          placeholder="Write an email to your friend about..."
                          className="w-full px-4 py-2.5 border border-purple-200 rounded-xl bg-white text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 transition-all resize-none"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-purple-800 mb-1.5">
                            Min sozlar
                          </label>
                          <input
                            type="number"
                            name="min_words"
                            value={itemForm.min_words}
                            onChange={handleItemChange}
                            min={0}
                            className="w-full px-4 py-2.5 border border-purple-200 rounded-xl bg-white text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 transition-all"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-purple-800 mb-1.5">
                            Max sozlar
                          </label>
                          <input
                            type="number"
                            name="max_words"
                            value={itemForm.max_words}
                            onChange={handleItemChange}
                            min={1}
                            className="w-full px-4 py-2.5 border border-purple-200 rounded-xl bg-white text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 transition-all"
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Speaking Task */}
                  {isSpeakingItem && (
                    <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 space-y-4">
                      <h3 className="text-sm font-semibold text-rose-900 flex items-center gap-2">
                        <Mic className="w-4 h-4" />
                        Speaking Task
                      </h3>
                      <div>
                        <label className="block text-xs font-medium text-rose-800 mb-1.5">
                          Mavzu / Topic <span className="text-red-500">*</span>
                        </label>
                        <textarea
                          name="question_text"
                          value={itemForm.question_text}
                          onChange={handleItemChange}
                          rows={3}
                          placeholder="Describe your favourite teacher..."
                          className="w-full px-4 py-2.5 border border-rose-200 rounded-xl bg-white text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 transition-all resize-none"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-rose-800 mb-1.5">
                          Qoshimcha koriqtnoma
                        </label>
                        <textarea
                          name="instruction"
                          value={itemForm.instruction}
                          onChange={handleItemChange}
                          rows={2}
                          placeholder="You have 30 seconds to prepare..."
                          className="w-full px-4 py-2.5 border border-rose-200 rounded-xl bg-white text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 transition-all resize-none"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs font-medium text-rose-800 mb-1.5">
                            Tayyorgarlik (sek)
                          </label>
                          <input
                            type="number"
                            name="preparation_time_sec"
                            value={itemForm.preparation_time_sec}
                            onChange={handleItemChange}
                            min={0}
                            max={300}
                            className="w-full px-4 py-2.5 border border-rose-200 rounded-xl bg-white text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 transition-all"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-rose-800 mb-1.5">
                            Gapirish (sek)
                          </label>
                          <input
                            type="number"
                            name="answer_time_sec"
                            value={itemForm.answer_time_sec}
                            onChange={handleItemChange}
                            min={10}
                            max={600}
                            className="w-full px-4 py-2.5 border border-rose-200 rounded-xl bg-white text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-rose-500/20 focus:border-rose-500 transition-all"
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Reading/Listening Question Text */}
                  {!isWritingItem && (
                    <div>
                      <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                        {isSpeakingItem ? 'Mavzu' : 'Savol matni'}
                      </label>
                      <textarea
                        name="question_text"
                        value={itemForm.question_text}
                        onChange={handleItemChange}
                        rows={2}
                        placeholder={isSpeakingItem ? 'Topic...' : 'What is the main idea?'}
                        className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all resize-none"
                      />
                    </div>
                  )}

                  {/* Options for Reading/Listening */}
                  {showOptions && (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label className="block text-sm font-semibold text-slate-900">
                          Variantlar
                        </label>
                        <button
                          type="button"
                          onClick={handleAddOption}
                          className="flex items-center gap-1 text-xs text-orange-600 hover:text-orange-700 font-medium"
                        >
                          <Plus className="w-3.5 h-3.5" />
                          Variant qoshish
                        </button>
                      </div>

                      <div className="space-y-2">
                        {itemOptions.map((opt, idx) => {
                          const letter = String.fromCharCode(65 + idx);
                          const isCorrect = opt.is_correct;

                          return (
                            <div key={idx} className="flex items-center gap-2">
                              <button
                                type="button"
                                onClick={() => handleOptionChange(idx, 'is_correct', !opt.is_correct)}
                                className={`flex-shrink-0 w-9 h-9 rounded-lg border-2 flex items-center justify-center transition-all text-xs font-bold ${
                                  isCorrect
                                    ? 'border-emerald-500 bg-emerald-500 text-white shadow-sm'
                                    : 'border-slate-200 bg-white text-slate-400 hover:border-emerald-400'
                                }`}
                                title="Togri javob"
                              >
                                {letter}
                              </button>
                              <input
                                type="text"
                                value={opt.text}
                                onChange={(e) => handleOptionChange(idx, 'text', e.target.value)}
                                placeholder={`Variant ${letter}`}
                                className={`flex-1 px-3 py-2 border rounded-xl text-sm focus:outline-none focus:ring-2 transition-all ${
                                  isCorrect
                                    ? 'border-emerald-300 bg-emerald-50 focus:ring-emerald-500/20'
                                    : 'border-slate-200 bg-slate-50 focus:ring-orange-500/20 focus:border-orange-500'
                                }`}
                              />
                              {itemOptions.length > 2 && (
                                <button
                                  type="button"
                                  onClick={() => handleRemoveOption(idx)}
                                  className="flex-shrink-0 p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              )}
                            </div>
                          );
                        })}
                      </div>

                      <div className="mt-3 p-3 bg-emerald-50 border border-emerald-100 rounded-xl">
                        <p className="text-xs text-emerald-800 flex items-start gap-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                          Harf ustiga bosib togri javobni belgilang. Yashil rangda korsatiladi.
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Order + Score */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                        Tartib
                      </label>
                      <input
                        type="number"
                        name="order"
                        value={itemForm.order}
                        onChange={handleItemChange}
                        min={1}
                        className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-900 mb-1.5">
                        Maks ball
                      </label>
                      <input
                        type="number"
                        name="max_score"
                        value={itemForm.max_score}
                        onChange={handleItemChange}
                        min={0}
                        step={0.5}
                        className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                      />
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-4 border-t border-slate-100">
                    <button
                      type="button"
                      onClick={handleCancelItem}
                      className="flex-1 px-4 py-2.5 text-sm font-medium text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-100 transition"
                    >
                      Bekor qilish
                    </button>
                    <button
                      type="submit"
                      disabled={savingItem}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl hover:from-orange-600 hover:to-orange-700 disabled:opacity-50 transition-all shadow-lg shadow-orange-500/20"
                    >
                      {savingItem ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Saqlanmoqda...
                        </>
                      ) : (
                        <>
                          <Save className="w-4 h-4" />
                          Saqlash
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </motion.form>
            )}
          </AnimatePresence>

          {/* Error */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-xl"
              >
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700 flex-1">{error}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}