"use client";

import { useCallback, useEffect, useState, FormEvent } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import AudioUpload from "@/app/exam/components/AudioUpload";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

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
  { value: "listening", label: "🎧 Listening" },
  { value: "reading", label: "📖 Reading" },
  { value: "writing", label: "✍️ Writing" },
  { value: "speaking", label: "🎤 Speaking" },
];

const ITEM_TYPE_LABELS: Record<string, string> = {
  listening_question: "🎧 Listening Question",
  reading_question: "📖 Reading Question",
  writing_task: "✍️ Writing Task",
  speaking_task: "🎤 Speaking Task",
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
  const [error, setError] = useState("");

  // ── Block form data ────────────────────────────────────
  const [blockForm, setBlockForm] = useState({
    title: "",
    description: "",
    instructions: "",
    block_type: "reading",
    passage_text: "",
    audio_url: "",
    order: 1,
    time_limit_sec: 600,
  });

  // ── Item form data ─────────────────────────────────────
  const [itemForm, setItemForm] = useState({
    item_type: "reading_question",
    title: "",
    instruction: "",
    question_text: "",
    min_words: 80,
    max_words: 120,
    preparation_time_sec: 30,
    answer_time_sec: 60,
    max_score: 1,
    order: 1,
  });

  const [itemOptions, setItemOptions] = useState<Option[]>([
    { text: "", is_correct: false, order: 1 },
    { text: "", is_correct: false, order: 2 },
    { text: "", is_correct: false, order: 3 },
    { text: "", is_correct: false, order: 4 },
  ]);

  // ── Ma'lumot yuklash ───────────────────────────────────
  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");

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
        setError("Block topilmadi");
        return;
      }

      setBlock(found);
      setBlockForm({
        title: found.title || "",
        description: found.description || "",
        instructions: found.instructions || "",
        block_type: found.block_type || "reading",
        passage_text: found.passage_text || "",
        audio_url: found.audio_url || "",
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
      console.error("Yuklash xatosi:", err);
      setError(err instanceof Error ? err.message : "Malumotlar yuklanmadi");
    } finally {
      setLoading(false);
    }
  }, [token, blockId, examId]);

  useEffect(() => {
    if (token) loadData();
  }, [token, blockId, loadData]);

  // ── Block handlers ─────────────────────────────────────
  function handleBlockChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) {
    const { name, value, type } = e.target;
    setBlockForm((prev) => ({
      ...prev,
      [name]: type === "number" ? Number(value) : value,
    }));
  }

  function handleBlockAudioUploaded(url: string) {
    setBlockForm((prev) => ({ ...prev, audio_url: url }));
  }

  async function handleSaveBlock(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSavingBlock(true);

    try {
      const res = await fetch(`${API_URL}/api/v2/exam/admin/blocks/${blockId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(blockForm),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      alert("✅ Block saqlandi!");
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Saqlashda xato");
    } finally {
      setSavingBlock(false);
    }
  }

  // ── Item handlers ──────────────────────────────────────
  function handleItemChange(
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) {
    const { name, value, type } = e.target;
    setItemForm((prev) => ({
      ...prev,
      [name]: type === "number" ? Number(value) : value,
    }));
  }

  function handleOptionChange(
    idx: number,
    field: "text" | "is_correct",
    value: string | boolean
  ) {
    setItemOptions((prev) =>
      prev.map((opt, i) => (i === idx ? { ...opt, [field]: value } : opt))
    );
  }

  function handleAddOption() {
    setItemOptions((prev) => [
      ...prev,
      { text: "", is_correct: false, order: prev.length + 1 },
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
      title: item.title || "",
      instruction: item.instruction || "",
      question_text: item.question_text || "",
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
        { text: "", is_correct: false, order: 1 },
        { text: "", is_correct: false, order: 2 },
        { text: "", is_correct: false, order: 3 },
        { text: "", is_correct: false, order: 4 },
      ]);
    }
  }

  function handleCreateNewItem() {
    const defaultItemType =
      block?.block_type === "listening"
        ? "listening_question"
        : block?.block_type === "reading"
        ? "reading_question"
        : block?.block_type === "writing"
        ? "writing_task"
        : "speaking_task";

    setSelectedItemId(null);
    setIsCreatingItem(true);
    setItemForm({
      item_type: defaultItemType,
      title: "",
      instruction: "",
      question_text: "",
      min_words: 80,
      max_words: 120,
      preparation_time_sec: 30,
      answer_time_sec: 60,
      max_score: 1,
      order: items.length + 1,
    });
    setItemOptions([
      { text: "", is_correct: false, order: 1 },
      { text: "", is_correct: false, order: 2 },
      { text: "", is_correct: false, order: 3 },
      { text: "", is_correct: false, order: 4 },
    ]);
  }

  function handleCancelItem() {
    setSelectedItemId(null);
    setIsCreatingItem(false);
  }

  async function handleSaveItem(e: FormEvent) {
    e.preventDefault();
    setSavingItem(true);
    setError("");

    try {
      const isChoiceType =
        itemForm.item_type === "reading_question" ||
        itemForm.item_type === "listening_question";

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

      if (itemForm.item_type === "writing_task") {
        payload.min_words = itemForm.min_words;
        payload.max_words = itemForm.max_words;
      }

      if (itemForm.item_type === "speaking_task") {
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
      const method = selectedItemId ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `HTTP ${res.status}`);
      }

      alert(selectedItemId ? "✅ Savol yangilandi" : "✅ Savol yaratildi");
      handleCancelItem();
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Saqlashda xato");
    } finally {
      setSavingItem(false);
    }
  }

  async function handleDeleteItem(itemId: number) {
    if (!confirm("Bu savolni o'chirishni xohlaysizmi?")) return;

    try {
      const res = await fetch(`${API_URL}/api/v2/exam/admin/items/${itemId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      setItems((prev) => prev.filter((item) => item.id !== itemId));
      if (selectedItemId === itemId) handleCancelItem();
    } catch (err) {
      alert(err instanceof Error ? err.message : "O'chirishda xato");
    }
  }

  if (loading) return <div className="p-6">Yuklanmoqda...</div>;
  if (!block)
    return <div className="p-6 text-red-600">{error || "Block topilmadi"}</div>;

  const showItemEditor = selectedItemId !== null || isCreatingItem;
  const isListening = blockForm.block_type === "listening";
  const isReading = blockForm.block_type === "reading";

  const isWritingItem = itemForm.item_type === "writing_task";
  const isSpeakingItem = itemForm.item_type === "speaking_task";
  const showOptions =
    itemForm.item_type === "reading_question" ||
    itemForm.item_type === "listening_question";

  return (
    <div className="flex flex-col bg-gray-50">
      {/* ═══ HEADER (sticky top) ═══ */}
      <header className="sticky top-0 z-20 bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push(`/exam/exams/${examId}`)}
            className="text-blue-600 hover:underline flex items-center gap-1"
          >
            ← Examga qaytish
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Block: {block.title}</h1>
        </div>
      </header>

      {/* ═══ MAIN CONTENT ═══ */}
      <div className="flex-1 flex">
        {/* ═══ CHAP USTUN: Savollar ro'yxati (sticky sidebar) ═══ */}
        <aside className="w-80 sticky top-[73px] h-[calc(100vh-73px)] bg-white border-r border-gray-200 flex flex-col overflow-hidden shrink-0">
          <div className="p-4 border-b border-gray-200">
            <button
              onClick={handleCreateNewItem}
              className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 font-semibold transition-colors"
            >
              + Yangi savol
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {items.length === 0 ? (
              <div className="text-center py-8 text-gray-500 text-sm">
                Hali savollar yo&apos;q
              </div>
            ) : (
              items.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleSelectItem(item.id)}
                  className={`p-3 rounded-lg cursor-pointer transition-all ${
                    selectedItemId === item.id
                      ? "bg-blue-100 border-2 border-blue-500 shadow-sm"
                      : "bg-gray-50 border-2 border-transparent hover:bg-gray-100 hover:shadow-sm"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-mono bg-gray-200 px-2 py-0.5 rounded">
                          #{item.order}
                        </span>
                        <span className="text-xs text-gray-500">
                          {ITEM_TYPE_LABELS[item.item_type]}
                        </span>
                      </div>
                      <h3 className="font-semibold text-sm truncate text-gray-900">
                        {item.title}
                      </h3>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteItem(item.id);
                      }}
                      className="text-red-500 hover:text-red-700 text-xs font-bold shrink-0"
                      title="O'chirish"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </aside>

        {/* ═══ O'NG USTUN: Block + Item editor (scrollable) ═══ */}
        <main className="flex-1 p-6 space-y-6 min-w-0">
          {/* ─── BLOCK SOZLAMALARI ─── */}
          <form
            onSubmit={handleSaveBlock}
            className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
          >
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-900">
              ⚙️ Block sozlamalari
            </h2>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1.5 text-gray-700">
                  Block turi
                </label>
                <select
                  name="block_type"
                  value={blockForm.block_type}
                  onChange={handleBlockChange}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {BLOCK_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5 text-gray-700">
                  Nomi <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="title"
                  value={blockForm.title}
                  onChange={handleBlockChange}
                  required
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-1.5 text-gray-700">
                Yoriqnoma (instructions)
              </label>
              <textarea
                name="instructions"
                value={blockForm.instructions}
                onChange={handleBlockChange}
                rows={2}
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {isReading && (
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1.5 text-gray-700">
                  📖 Passage (matn)
                </label>
                <textarea
                  name="passage_text"
                  value={blockForm.passage_text}
                  onChange={handleBlockChange}
                  rows={6}
                  placeholder="Reading uchun matn shu yerga yoziladi..."
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            )}

            {isListening && (
              <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold mb-3 text-blue-900">🎧 Audio fayl</h3>
                <AudioUpload
                  currentUrl={blockForm.audio_url}
                  onUpload={handleBlockAudioUploaded}
                />
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1.5 text-gray-700">Tartib</label>
                <input
                  type="number"
                  name="order"
                  value={blockForm.order}
                  onChange={handleBlockChange}
                  min={1}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5 text-gray-700">
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
                  className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={savingBlock}
              className="w-full bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold transition-colors"
            >
              {savingBlock ? "Saqlanmoqda..." : "💾 Blockni saqlash"}
            </button>
          </form>

          {/* ─── ITEM EDITOR ─── */}
          {showItemEditor && (
            <form
              onSubmit={handleSaveItem}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  {selectedItemId ? "✏️ Savolni tahrirlash" : "➕ Yangi savol"}
                </h2>
                <button
                  type="button"
                  onClick={handleCancelItem}
                  className="text-gray-500 hover:text-gray-700 text-sm font-medium"
                >
                  ✕ Yopish
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5 text-gray-700">
                    Savol turi
                  </label>
                  <select
                    name="item_type"
                    value={itemForm.item_type}
                    onChange={handleItemChange}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="reading_question">📖 Reading Question</option>
                    <option value="listening_question">🎧 Listening Question</option>
                    <option value="writing_task">✍️ Writing Task</option>
                    <option value="speaking_task">🎤 Speaking Task</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5 text-gray-700">
                    Sarlavha <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    name="title"
                    value={itemForm.title}
                    onChange={handleItemChange}
                    required
                    placeholder="Masalan: Question 1"
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              {!isWritingItem && (
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-1.5 text-gray-700">
                    {isSpeakingItem ? "🎤 Mavzu / Topic" : "Savol matni"}
                  </label>
                  <textarea
                    name="question_text"
                    value={itemForm.question_text}
                    onChange={handleItemChange}
                    rows={isSpeakingItem ? 3 : 2}
                    placeholder={
                      isSpeakingItem
                        ? "Describe your favourite teacher."
                        : "What is the main idea?"
                    }
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              )}

              {isWritingItem && (
                <div className="mb-4 bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h3 className="font-semibold mb-3 text-purple-900">
                    ✍️ Writing Task Sozlamalari
                  </h3>

                  <div className="mb-4">
                    <label className="block text-sm font-medium mb-1.5 text-gray-700">
                      Writing topshirigi <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      name="question_text"
                      value={itemForm.question_text}
                      onChange={handleItemChange}
                      required
                      rows={4}
                      placeholder="Write an email to your friend about your last holiday. Write 80-120 words."
                      className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1.5 text-gray-700">
                        Min so&apos;zlar soni
                      </label>
                      <input
                        type="number"
                        name="min_words"
                        value={itemForm.min_words}
                        onChange={handleItemChange}
                        min={0}
                        className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1.5 text-gray-700">
                        Max so&apos;zlar soni
                      </label>
                      <input
                        type="number"
                        name="max_words"
                        value={itemForm.max_words}
                        onChange={handleItemChange}
                        min={1}
                        className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                      />
                    </div>
                  </div>
                </div>
              )}

              {isSpeakingItem && (
                <div className="mb-4 bg-rose-50 border border-rose-200 rounded-lg p-4">
                  <h3 className="font-semibold mb-3 text-rose-900">
                    🎤 Speaking Task Sozlamalari
                  </h3>

                  <div className="mb-4">
                    <label className="block text-sm font-medium mb-1.5 text-gray-700">
                      Qo&apos;shimcha ko&apos;rsatma (instruction)
                    </label>
                    <textarea
                      name="instruction"
                      value={itemForm.instruction}
                      onChange={handleItemChange}
                      rows={2}
                      placeholder="You have 30 seconds to prepare. Speak for 60 seconds."
                      className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1.5 text-gray-700">
                        ⏱️ Tayyorgarlik vaqti (sekund)
                      </label>
                      <input
                        type="number"
                        name="preparation_time_sec"
                        value={itemForm.preparation_time_sec}
                        onChange={handleItemChange}
                        min={0}
                        max={300}
                        className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1.5 text-gray-700">
                        🎙️ Gapirish vaqti (sekund)
                      </label>
                      <input
                        type="number"
                        name="answer_time_sec"
                        value={itemForm.answer_time_sec}
                        onChange={handleItemChange}
                        min={10}
                        max={600}
                        className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
                      />
                    </div>
                  </div>

                  <p className="text-xs text-rose-600 mt-3">
                    💡 Speaking uchun variant (option) kerak emas — foydalanuvchi
                    mavzu bo&apos;yicha ovoz yozadi.
                  </p>
                </div>
              )}

              {showOptions && (
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Variantlar
                    </label>
                    <button
                      type="button"
                      onClick={handleAddOption}
                      className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                    >
                      + Variant qo&apos;shish
                    </button>
                  </div>

                  <div className="space-y-2">
                    {itemOptions.map((opt, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={opt.is_correct}
                          onChange={(e) =>
                            handleOptionChange(
                              idx,
                              "is_correct",
                              e.target.checked
                            )
                          }
                          className="w-5 h-5 text-emerald-600 rounded"
                          title="To'g'ri javob"
                        />
                        <input
                          type="text"
                          value={opt.text}
                          onChange={(e) =>
                            handleOptionChange(idx, "text", e.target.value)
                          }
                          placeholder={`Variant ${String.fromCharCode(65 + idx)}`}
                          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                        <span
                          className={`text-xs font-semibold px-2 py-1 rounded ${
                            opt.is_correct
                              ? "bg-emerald-100 text-emerald-700"
                              : "bg-slate-100 text-slate-500"
                          }`}
                        >
                          {String.fromCharCode(65 + idx)}
                        </span>
                        {itemOptions.length > 2 && (
                          <button
                            type="button"
                            onClick={() => handleRemoveOption(idx)}
                            className="text-red-500 hover:text-red-700 font-bold shrink-0"
                            title="O'chirish"
                          >
                            ✕
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium mb-1.5 text-gray-700">
                    Tartib
                  </label>
                  <input
                    type="number"
                    name="order"
                    value={itemForm.order}
                    onChange={handleItemChange}
                    min={1}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1.5 text-gray-700">
                    Maks ball
                  </label>
                  <input
                    type="number"
                    name="max_score"
                    value={itemForm.max_score}
                    onChange={handleItemChange}
                    min={0}
                    step={0.5}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={handleCancelItem}
                  className="px-6 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium text-gray-700 transition-colors"
                >
                  Bekor qilish
                </button>
                <button
                  type="submit"
                  disabled={savingItem}
                  className="flex-1 bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold transition-colors"
                >
                  {savingItem ? "Saqlanmoqda..." : "💾 Saqlash"}
                </button>
              </div>
            </form>
          )}

          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg border border-red-200">
              ❌ {error}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}