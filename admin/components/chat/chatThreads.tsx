import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface ChatThreadsProps {
  userId: number | string;
}

interface Thread {
  id: number;
  title: string;
  messages?: Message[];
}

interface Message {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatThreads({ userId }: ChatThreadsProps) {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [selectedThread, setSelectedThread] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Thread'larni olish
  useEffect(() => {
    const fetchThreads = async () => {
      const response = await axios.get(
        `/api/conversations/threads?user_id=${userId}`
      );
      setThreads(response.data);
    };
    fetchThreads();
  }, [userId]);

  // Mavjud thread'ni tanlash
  const handleSelectThread = async (threadId: number) => {
    setSelectedThread(threadId);
    setLoading(true);

    const response = await axios.get(
      `/api/conversations/threads/${threadId}/messages`
    );
    setMessages(response.data);
    setLoading(false);
  };

  // Yangi xabar yuborish
  const handleSendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    const response = await axios.post(
      `/api/conversations/threads/${selectedThread}/messages`,
      { user_id: userId, content: input }
    );

    setMessages([
      ...messages,
      response.data.user_message,
      response.data.assistant_message
    ]);
    setInput('');
    setLoading(false);
  };

  return (
    <div className="flex gap-4 h-screen">
      {/* Chapda thread'lar ro'yxati */}
      <div className="w-64 bg-dark-50 p-4 overflow-y-auto rounded-2xl border border-dark-200">
        <h3 className="font-bold mb-4">💬 Suhbatlar</h3>
        {threads.map((thread) => (
          <button
            key={thread.id}
            onClick={() => handleSelectThread(thread.id)}
            className={`w-full text-left p-2 mb-2 rounded-lg ${
              selectedThread === thread.id
                ? 'bg-primary-600 text-white'
                : 'bg-white hover:bg-dark-100'
            }`}
          >
            <div className="font-semibold">{thread.title}</div>
            <div className="text-xs text-gray-500">
              {thread.messages?.length || 0} xabar
            </div>
          </button>
        ))}
        <button className="w-full mt-4 p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition">
          ➕ Yangi suhbat
        </button>
      </div>

      {/* O'ng tarafda suhbat oynasi */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-4 bg-white rounded-3xl border border-dark-200">
          {messages.map((msg, idx) => (
            <div key={idx} className={`mb-4 ${msg.role === 'assistant' ? 'text-left' : 'text-right'}`}>
              <div
                className={`inline-block p-3 rounded-lg ${
                  msg.role === 'assistant'
                    ? 'bg-dark-50 text-dark-900'
                    : 'bg-primary-600 text-white'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {loading && <div className="text-center text-dark-500">⏳ Javob kutilmoqda...</div>}
        </div>

        {/* Input field */}
        <form onSubmit={handleSendMessage} className="p-4 border-t border-dark-200">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Xabar yozing..."
              className="flex-1 p-2 border border-dark-200 rounded-lg bg-dark-50"
              disabled={loading}
            />
            <button
              type="submit"
              className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
              disabled={loading}
            >
              📤 Yuborish
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
