'use client';

import { useState, useEffect, FormEvent, ChangeEvent } from 'react';
import { Dialog } from '@/components/ui/Dialog';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { ContentItem } from '@/lib/types';
import { Upload, FileText } from 'lucide-react';

interface EditContentModalProps {
  isOpen: boolean;
  item: ContentItem | null;
  onClose: () => void;
  onSave: (id: number, formData: FormData) => void;
  isLoading: boolean;
}

export function EditContentModal({ isOpen, item, onClose, onSave, isLoading }: EditContentModalProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);

  // Modal ochilganda eski malumotlarni toldirish
  useEffect(() => {
    if (item) {
      setTitle(item.title);
      setDescription(item.description || '');
      setFile(null);
    }
  }, [item, isOpen]);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!item) return;

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    if (file) {
      formData.append('file', file);
    }

    onSave(item.id, formData);
  };

  return (
    <Dialog isOpen={isOpen} onClose={onClose} title="Contentni tahrirlash" size="lg">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Sarlavha */}
        <Input
          label="Sarlavha"
          placeholder="Masalan: Python 1-dars"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />

        {/* Izoh */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Izoh
          </label>
          <textarea
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary transition-colors min-h-[100px]"
            placeholder="Dars haqida qisqa izoh..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        {/* Fayl (ixtiyoriy) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Yangi fayl (ixtiyoriy)
          </label>
          <label className="flex items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-primary hover:bg-orange-50 transition-colors">
            <div className="flex flex-col items-center gap-2 text-gray-500">
              <Upload size={24} />
              <span className="text-sm">
                {file ? file.name : "Faylni almashtirish uchun bosing"}
              </span>
              {file && (
                <span className="text-xs text-gray-400">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </span>
              )}
              {!file && item && (
                <span className="text-xs text-gray-400 flex items-center gap-1">
                  <FileText size={12} />
                  Joriy: {item.content_type === 'video' ? 'Video' : 'File'}
                </span>
              )}
            </div>
            <input
              type="file"
              className="sr-only"
              accept={item?.content_type === 'video' ? 'video/*' : '*/*'}
              onChange={handleFileChange}
            />
          </label>
          <p className="mt-1 text-xs text-gray-400">
            Agar yangi fayl tanlamasangiz, faqat matn malumotnlari yangilanadi.
          </p>
        </div>

        {/* Tugmalar */}
        <div className="flex gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Bekor qilish
          </button>
          <Button type="submit" isLoading={isLoading} className="flex-1">
            Saqlash
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
