"use client";

import { useEffect, useState, FormEvent } from "react";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

interface Option {
  id: number;
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
  passage_text?: string;
  audio_url?: string;
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

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [newOptionTexts, setNewOptionTexts] = useState<
    Record<number, string>
  >({});

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    instructions: "",
    block_type: "reading",
    order: 1,
    time_limit_sec: 600,
  });

  const [showAddItem, setShowAddItem] = useState(false);

  const [newItem, setNewItem] = useState({
    title: "",
    question_text: "",
    passage_text: "",
    item_type: "reading_question",
  });

  const loadData = async () => {
    setLoading(true);
    setError("");

    try {
      const headers = {
        Authorization: `Bearer ${token}`,
      };

      const blocksRes = await fetch(
        `${API_URL}/api/v2/exam/admin/exams/${examId}/blocks`,
        {
          headers,
        }
      );

      if (!blocksRes.ok) {
        throw new Error(`HTTP ${blocksRes.status}`);
      }

      const blocks = await blocksRes.json();

      const found = blocks.find(
        (b: Block) => b.id === blockId
      );

      if (!found) {
        setError("Block topilmadi");
        return;
      }

      setBlock(found);

      setFormData({
        title: found.title || "",
        description: found.description || "",
        instructions: found.instructions || "",
        block_type: found.block_type || "reading",
        order: found.order || 1,
        time_limit_sec: found.time_limit_sec || 600,
      });

      const itemsRes = await fetch(
        `${API_URL}/api/v2/exam/admin/blocks/${blockId}/items`,
        {
          headers,
        }
      );

      if (itemsRes.ok) {
        const itemsData = await itemsRes.json();

        setItems(
          Array.isArray(itemsData)
            ? itemsData
            : itemsData.items || []
        );
      }
    } catch (err) {
      console.error("Yuklash xatosi:", err);

      setError(
        err instanceof Error
          ? err.message
          : "Malumotlar yuklanmadi"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      loadData();
    }
  }, [token, blockId]);

  function handleChange(
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) {
    const { name, value, type } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]:
        type === "number"
          ? Number(value)
          : value,
    }));
  }

  async function handleSaveBlock(e: FormEvent) {
    e.preventDefault();

    setError("");
    setSaving(true);

    try {
      const res = await fetch(
        `${API_URL}/api/v2/exam/admin/blocks/${blockId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(formData),
        }
      );

      if (!res.ok) {
        throw new Error(
          `HTTP ${res.status}`
        );
      }

      alert("Block saqlandi!");

      await loadData();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Saqlashda xato"
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleAddItem() {
    if (!newItem.title.trim()) {
      alert("Savol matnini kiriting");
      return;
    }

    try {
      const res = await fetch(
        `${API_URL}/api/v2/exam/admin/blocks/${blockId}/items`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(newItem),
        }
      );

      if (!res.ok) {
        const data = await res.json().catch(() => null);

        throw new Error(
          data?.detail ||
            `HTTP ${res.status}`
        );
      }

      setShowAddItem(false);

      setNewItem({
        title: "",
        question_text: "",
        passage_text: "",
        item_type: "reading_question",
      });

      await loadData();
    } catch (err) {
      alert(
        err instanceof Error
          ? err.message
          : "Savol qoshishda xato"
      );
    }
  }

  async function handleDeleteItem(itemId: number) {
    const confirmed = confirm(
      "Bu savolni va uning barcha variantlarini ochirishni xohlaysizmi?"
    );

    if (!confirmed) {
      return;
    }

    try {
      const res = await fetch(
        `${API_URL}/api/v2/exam/admin/items/${itemId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!res.ok) {
        throw new Error(
          `HTTP ${res.status}`
        );
      }

      setItems((prev) =>
        prev.filter(
          (item) => item.id !== itemId
        )
      );
    } catch (err) {
      alert(
        err instanceof Error
          ? err.message
          : "Ochirishda xato"
      );
    }
  }

  async function handleAddOption(itemId: number) {
    const text =
      newOptionTexts[itemId]?.trim() || "";

    if (!text) {
      return;
    }

    try {
      const res = await fetch(
        `${API_URL}/api/v2/exam/admin/items/${itemId}/options`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            text,
            is_correct: false,
          }),
        }
      );

      if (!res.ok) {
        const data = await res.json().catch(() => null);

        throw new Error(
          data?.detail ||
            `HTTP ${res.status}`
        );
      }

      setNewOptionTexts((prev) => ({
        ...prev,
        [itemId]: "",
      }));

      await loadData();
    } catch (err) {
      alert(
        err instanceof Error
          ? err.message
          : "Variant qoshishda xato"
      );
    }
  }

  async function handleToggleCorrect(
    optionId: number,
    currentValue: boolean
  ) {
    try {
      const res = await fetch(
        `${API_URL}/api/v2/exam/admin/options/${optionId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            is_correct: !currentValue,
          }),
        }
      );

      if (!res.ok) {
        const data = await res.json().catch(() => null);

        throw new Error(
          data?.detail ||
            `HTTP ${res.status}`
        );
      }

      await loadData();
    } catch (err) {
      alert(
        err instanceof Error
          ? err.message
          : "Javob holatini ozgartirishda xato"
      );
    }
  }

  async function handleDeleteOption(
    optionId: number,
    itemId: number
  ) {
    const confirmed = confirm(
      "Bu variantni ochirishni xohlaysizmi?"
    );

    if (!confirmed) {
      return;
    }

    try {
      const res = await fetch(
        `${API_URL}/api/v2/exam/admin/options/${optionId}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!res.ok) {
        throw new Error(
          `HTTP ${res.status}`
        );
      }

      await loadData();
    } catch (err) {
      alert(
        err instanceof Error
          ? err.message
          : "Variant ochirishda xato"
      );
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        Yuklanmoqda...
      </div>
    );
  }

  if (!block) {
    return (
      <div className="p-6 text-red-600">
        {error || "Block topilmadi"}
      </div>
    );
  }

  return (
  <div className="p-6 max-w-4xl mx-auto space-y-6">
      <button
        type="button"
        onClick={() =>
          router.push(
            `/exam/exams/${examId}`
          )
        }
        className="text-blue-600 mb-4 inline-block hover:underline"
      >
        ← Examga qaytish
      </button>

      <h1 className="text-3xl font-bold mb-6">
        Block tahrirlash
      </h1>

      <form
        onSubmit={handleSaveBlock}
        className="bg-white rounded-lg shadow p-6 space-y-5 mb-8"
      >
        <div>
          <label className="block text-sm font-medium mb-1.5">
            Block turi
          </label>

          <select
            name="block_type"
            value={formData.block_type}
            onChange={handleChange}
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
          >
            {BLOCK_TYPES.map((type) => (
              <option
                key={type.value}
                value={type.value}
              >
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1.5">
            Nomi *
          </label>

          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1.5">
            Yoriqnoma
          </label>

          <textarea
            name="instructions"
            value={formData.instructions}
            onChange={handleChange}
            rows={2}
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">
              Tartib
            </label>

            <input
              type="number"
              name="order"
              value={formData.order}
              onChange={handleChange}
              min={1}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1.5">
              Vaqt (daq)
            </label>

            <input
              type="number"
              value={Math.floor(
                formData.time_limit_sec / 60
              )}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  time_limit_sec:
                    Number(e.target.value) * 60,
                }))
              }
              min={1}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5"
            />
          </div>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg">
            ❌ {error}
          </div>
        )}

        <button
          type="submit"
          disabled={saving}
          className="w-full bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {saving
            ? "Saqlanmoqda..."
            : "💾 Blockni saqlash"}
        </button>
      </form>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            Savollar ({items.length})
          </h2>

          <button
            onClick={() => router.push(`/exam/exams/${examId}/blocks/${blockId}/items/new`)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
          >
            + Savol qo&rsquo;shish
          </button>
        </div>

        {items.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Hali savollar qoshilmagan.
          </div>
        ) : (
          <div className="space-y-4">
            {items.map((item) => (
              <div
                key={item.id}
                className="border rounded-lg p-4"
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded">
                        #{item.order}
                      </span>

                      <span className="text-xs text-gray-500">
                        {ITEM_TYPE_LABELS[
                          item.item_type
                        ] || item.item_type}
                      </span>
                    </div>

                    <h3 className="font-semibold">
                      {item.title}
                    </h3>

                    {item.question_text && (
                      <p className="text-sm text-gray-700 mt-1">
                        {item.question_text}
                      </p>
                    )}
                  </div>

                  <button
                    type="button"
                    onClick={() =>
                      handleDeleteItem(item.id)
                    }
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Ochirish
                  </button>
                </div>

                {/* Options */}
                {(item.item_type ===
                  "reading_question" ||
                  item.item_type ===
                    "listening_question") && (
                  <div className="mt-3 pl-4 border-l-2 border-gray-200">
                    <div className="text-xs font-semibold text-gray-500 mb-2">
                      VARIANTLAR ({item.options.length}):
                    </div>

                    {item.options.length > 0 ? (
                      <div className="space-y-2 mb-3">
                        {item.options.map(
                          (opt) => (
                            <div
                              key={opt.id}
                              className={`flex items-center gap-2 text-sm p-2 rounded ${
                                opt.is_correct
                                  ? "bg-green-50 border border-green-200"
                                  : "bg-gray-50"
                              }`}
                            >
                              <button
                                type="button"
                                onClick={() =>
                                  handleToggleCorrect(
                                    opt.id,
                                    opt.is_correct
                                  )
                                }
                                className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${
                                  opt.is_correct
                                    ? "bg-green-500 text-white"
                                    : "bg-gray-300 text-white hover:bg-gray-400"
                                }`}
                                title={
                                  opt.is_correct
                                    ? "To&rsquo;g&rsquo;ri javob"
                                    : "Notogri javob"
                                }
                              >
                                {opt.is_correct
                                  ? "✓"
                                  : ""}
                              </button>

                              <span className="flex-1">
                                {opt.text}
                              </span>

                              {opt.is_correct && (
                                <span className="text-xs text-green-600 font-semibold">
                                  To&rsquo;g&rsquo;ri
                                </span>
                              )}

                              <button
                                type="button"
                                onClick={() =>
                                  handleDeleteOption(
                                    opt.id,
                                    item.id
                                  )
                                }
                                className="text-red-500 hover:text-red-700 text-xs font-bold"
                                title="Ochirish"
                              >
                                ✕
                              </button>
                            </div>
                          )
                        )}
                      </div>
                    ) : (
                      <p className="text-xs text-gray-400 mb-3">
                        Hali variantlar yoq
                      </p>
                    )}

                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={
                          newOptionTexts[
                            item.id
                          ] || ""
                        }
                        onChange={(e) =>
                          setNewOptionTexts(
                            (prev) => ({
                              ...prev,
                              [item.id]:
                                e.target.value,
                            })
                          )
                        }
                        onKeyDown={(e) => {
                          if (
                            e.key === "Enter"
                          ) {
                            e.preventDefault();
                            handleAddOption(
                              item.id
                            );
                          }
                        }}
                        placeholder="Yangi variant matni..."
                        className="flex-1 border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500"
                      />

                      <button
                        type="button"
                        onClick={() =>
                          handleAddOption(
                            item.id
                          )
                        }
                        className="bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 text-sm"
                      >
                        + Qoshish
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add item modal */}
      {showAddItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
            <h3 className="text-xl font-bold mb-4">
              Yangi savol qoshish
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Savol turi
                </label>

                <select
                  value={newItem.item_type}
                  onChange={(e) =>
                    setNewItem((prev) => ({
                      ...prev,
                      item_type:
                        e.target.value,
                    }))
                  }
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="reading_question">
                    📖 Reading Question
                  </option>

                  <option value="listening_question">
                    🎧 Listening Question
                  </option>

                  <option value="writing_task">
                    ✍️ Writing Task
                  </option>

                  <option value="speaking_task">
                    🎤 Speaking Task
                  </option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Savol matni *
                </label>

                <input
                  type="text"
                  value={newItem.title}
                  onChange={(e) =>
                    setNewItem((prev) => ({
                      ...prev,
                      title:
                        e.target.value,
                    }))
                  }
                  placeholder="Masalan: What is the main idea?"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">
                  Toliq savol
                </label>

                <textarea
                  value={
                    newItem.question_text
                  }
                  onChange={(e) =>
                    setNewItem((prev) => ({
                      ...prev,
                      question_text:
                        e.target.value,
                    }))
                  }
                  rows={2}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>

              {newItem.item_type ===
                "reading_question" && (
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Passage
                  </label>

                  <textarea
                    value={
                      newItem.passage_text
                    }
                    onChange={(e) =>
                      setNewItem((prev) => ({
                        ...prev,
                        passage_text:
                          e.target.value,
                      }))
                    }
                    rows={4}
                    placeholder="Reading uchun matn..."
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
              )}
            </div>

            <div className="flex gap-3 mt-6">
              <button
                type="button"
                onClick={() =>
                  setShowAddItem(false)
                }
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Bekor qilish
              </button>

              <button
                type="button"
                onClick={handleAddItem}
                className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
              >
                ✅ Qoshish
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
