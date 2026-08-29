'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

interface BotText {
  id: number;
  key: string;
  lang: string;
  text: string;
  updated_at: string;
}

export default function BotTextsPage() {
  const [texts, setTexts] = useState<BotText[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editText, setEditText] = useState('');
  const [filterLang, setFilterLang] = useState<string>('all');
  const [filterKey, setFilterKey] = useState('');
  const router = useRouter();

  const fetchTexts = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterLang !== 'all') params.append('lang', filterLang);
      if (filterKey) params.append('key', filterKey);
      
      const res = await fetch(`/api/bot-texts${params}`);
      if (res.ok) {
        const data = await res.json();
        setTexts(data);
      }
    } catch (error) {
      console.error('Error fetching texts:', error);
    } finally {
      setLoading(false);
    }
  }, [filterLang, filterKey]);

  useEffect(() => {
    fetchTexts();
  }, [fetchTexts]);

  const handleEdit = (text: BotText) => {
    setEditingId(text.id);
    setEditText(text.text);
  };

  const handleSave = async (id: number) => {
    try {
      const res = await fetch(`/api/bot-texts/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: editText }),
      });
      
      if (res.ok) {
        setEditingId(null);
        fetchTexts();
      }
    } catch (error) {
      console.error('Error updating text:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure?')) return;
    
    try {
      const res = await fetch(`/api/bot-texts/${id}`, {
        method: 'DELETE',
      });
      
      if (res.ok) {
        fetchTexts();
      }
    } catch (error) {
      console.error('Error deleting text:', error);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Bot Texts (CMS)</h1>
      
      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <select
          value={filterLang}
          onChange={(e) => setFilterLang(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="all">All Languages</option>
          <option value="uz">Uzbek</option>
          <option value="ru">Russian</option>
          <option value="en">English</option>
        </select>
        
        <input
          type="text"
          placeholder="Filter by key..."
          value={filterKey}
          onChange={(e) => setFilterKey(e.target.value)}
          className="border rounded px-3 py-2 flex-1"
        />
      </div>

      {/* Table */}
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border">
            <thead>
              <tr className="bg-gray-100">
                <th className="border p-2">ID</th>
                <th className="border p-2">Key</th>
                <th className="border p-2">Lang</th>
                <th className="border p-2">Text</th>
                <th className="border p-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {texts.map((text) => (
                <tr key={text.id}>
                  <td className="border p-2">{text.id}</td>
                  <td className="border p-2 font-mono text-sm">{text.key}</td>
                  <td className="border p-2">{text.lang}</td>
                  <td className="border p-2">
                    {editingId === text.id ? (
                      <textarea
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        className="w-full border rounded p-2"
                        rows={3}
                      />
                    ) : (
                      <div className="max-w-md truncate">{text.text}</div>
                    )}
                  </td>
                  <td className="border p-2">
                    {editingId === text.id ? (
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleSave(text.id)}
                          className="bg-green-500 text-white px-3 py-1 rounded"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="bg-gray-500 text-white px-3 py-1 rounded"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleEdit(text)}
                          className="bg-blue-500 text-white px-3 py-1 rounded"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(text.id)}
                          className="bg-red-500 text-white px-3 py-1 rounded"
                        >
                          Delete
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
