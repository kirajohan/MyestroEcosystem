'use client';

import { useState, FormEvent, ChangeEvent } from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { ContentTable } from '@/components/content/ContentTable';
import { EditContentModal } from '@/components/content/EditContentModal';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';
import { toast } from 'sonner';
import { useContentList, useCreateContent, useUpdateContent, useDeleteContent } from '@/hooks/useContent';
import { ContentItem } from '@/lib/types';
import { Video, FileText, Upload, CheckCircle, List, AlertCircle, RefreshCw } from 'lucide-react';

export default function ContentPage() {
  // Upload form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [contentType, setContentType] = useState<'video' | 'file'>('video');
  const [file, setFile] = useState<File | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  // Table / modal / confirm state
  const [editItem, setEditItem] = useState<ContentItem | null>(null);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [deleteItem, setDeleteItem] = useState<ContentItem | null>(null);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);

  const { data: contents, isLoading: isListLoading, refetch: refetchContents } = useContentList();
  const createMutation = useCreateContent();
  const updateMutation = useUpdateContent();
  const deleteMutation = useDeleteContent();

  // Upload handlers
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadSuccess(false);
      setUploadError(null);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!file) {
      toast.error('Faylni tanlang');
      return;
    }
    if (!title.trim()) {
      toast.error('Sarlavhani kiriting');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('content_type', contentType);
    formData.append('file', file);

    setIsUploading(true);
    setUploadError(null);

    try {
      // useCreateContent hook orqali /api/content (Next.js proxy) ga yuboriladi
      // fetch + FormData ishlatiladi, Content-Type avtomatik multipart/form-data
      const data = await createMutation.mutateAsync(formData);

      toast.success(`Muvaffaqiyatli yuklandi! file_id: ${data.telegram_file_id?.slice(0, 20) || ''}...`);
      setUploadSuccess(true);

      // Formani tozalash
      setTitle('');
      setDescription('');
      setFile(null);
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

      // Refresh content list
      await refetchContents();

    } catch (err: any) {
      const errorMessage = err.message || 'Yuklashda xatolik';
      setUploadError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRetry = async () => {
    if (!file || !title.trim()) {
      toast.error('Qayta urinish uchun fayl va sarlavha kerak');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('content_type', contentType);
    formData.append('file', file);

    setIsUploading(true);
    setUploadError(null);

    try {
      const data = await createMutation.mutateAsync(formData);
      toast.success(`Qayta urinish muvaffaqiyatli! file_id: ${data.telegram_file_id?.slice(0, 20) || ''}...`);
      setUploadSuccess(true);
      setUploadError(null);

      // Formani tozalash
      setTitle('');
      setDescription('');
      setFile(null);
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

      // Refresh content list
      await refetchContents();

    } catch (err: any) {
      const errorMessage = err.message || 'Qayta urinishda xatolik';
      setUploadError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  // Edit handlers
  const handleEdit = (item: ContentItem) => {
    setEditItem(item);
    setIsEditOpen(true);
  };

  const handleSaveEdit = async (id: number, formData: FormData) => {
    try {
      await updateMutation.mutateAsync({ id, formData });
      toast.success('Muvaffaqiyatli saqlandi');
      setIsEditOpen(false);
      setEditItem(null);
    } catch (err: any) {
      toast.error(err.message || 'Tahrirlashda xatolik');
    }
  };

  // Delete handlers
  const handleDeleteClick = (item: ContentItem) => {
    setDeleteItem(item);
    setIsConfirmOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!deleteItem) return;
    try {
      await deleteMutation.mutateAsync(deleteItem.id);
      toast.success("O'chirildi");
      setIsConfirmOpen(false);
      setDeleteItem(null);
    } catch (err: any) {
      toast.error(err.message || "O'chirishda xatolik");
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Content Yuklash</h1>
        <p className="text-gray-600 mt-1">
          Video yoki faylni Telegram kanaliga yuklash va bazaga saqlash
        </p>
      </div>

      {/* Upload Form */}
      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Turi */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Turi
            </label>
            <div className="flex gap-4">
              <label
                className={`flex items-center gap-2 px-4 py-3 rounded-lg border-2 cursor-pointer transition-colors ${
                  contentType === 'video'
                    ? 'border-primary bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="radio"
                  name="content_type"
                  value="video"
                  checked={contentType === 'video'}
                  onChange={() => setContentType('video')}
                  className="sr-only"
                />
                <Video size={20} className={contentType === 'video' ? 'text-primary' : 'text-gray-400'} />
                <span className="font-medium">Video darslik</span>
              </label>

              <label
                className={`flex items-center gap-2 px-4 py-3 rounded-lg border-2 cursor-pointer transition-colors ${
                  contentType === 'file'
                    ? 'border-primary bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="radio"
                  name="content_type"
                  value="file"
                  checked={contentType === 'file'}
                  onChange={() => setContentType('file')}
                  className="sr-only"
                />
                <FileText size={20} className={contentType === 'file' ? 'text-primary' : 'text-gray-400'} />
                <span className="font-medium">File</span>
              </label>
            </div>
          </div>

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

          {/* Fayl */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Fayl
            </label>
            <label className="flex items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-primary hover:bg-dark-100 transition-colors">
              <div className="flex flex-col items-center gap-2 text-gray-500">
                <Upload size={24} />
                <span className="text-sm">
                  {file ? file.name : 'Faylni tanlash uchun bosing'}
                </span>
                {file && (
                  <span className="text-xs text-gray-400">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                )}
              </div>
              <input
                id="file-input"
                type="file"
                className="sr-only"
                accept={contentType === 'video' ? 'video/*' : '*/*'}
                onChange={handleFileChange}
              />
            </label>
          </div>

          {/* Success */}
          {uploadSuccess && (
            <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700">
              <CheckCircle size={18} />
              <span className="text-sm font-medium">Muvaffaqiyatli yuklandi!</span>
            </div>
          )}

          {/* Error */}
          {uploadError && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
              <AlertCircle size={18} className="mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium">Yuklashda xatolik</p>
                <p className="text-xs mt-1">{uploadError}</p>
              </div>
            </div>
          )}

          {/* Tugma */}
          <div className="flex gap-2">
            <Button 
              type="submit" 
              isLoading={isUploading || createMutation.isPending} 
              className="flex-1"
              disabled={isUploading}
            >
              {isUploading ? 'Yuklanmoqda...' : 'Yuklash'}
            </Button>
            
            {uploadError && (
              <Button
                type="button"
                onClick={handleRetry}
                isLoading={isUploading}
                disabled={isUploading}
                className="flex items-center gap-2"
              >
                <RefreshCw size={16} />
                Qayta urinish
              </Button>
            )}
          </div>
        </form>
      </Card>

      {/* Content List */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <List size={20} className="text-primary" />
          <h2 className="text-xl font-bold text-gray-900">Saqlangan contentlar</h2>
          <span className="ml-2 px-2 py-1 bg-gray-100 text-gray-600 text-sm rounded-full">
            {contents?.length || 0}
          </span>
        </div>

        <ContentTable
          items={contents || []}
          isLoading={isListLoading}
          onEdit={handleEdit}
          onDelete={handleDeleteClick}
        />
      </div>

      {/* Edit Modal */}
      <EditContentModal
        isOpen={isEditOpen}
        item={editItem}
        onClose={() => {
          setIsEditOpen(false);
          setEditItem(null);
        }}
        onSave={handleSaveEdit}
        isLoading={updateMutation.isPending}
      />

      {/* Delete Confirm Dialog */}
      <ConfirmDialog
        isOpen={isConfirmOpen}
        title="Contentni o'chirish"
        message={`"${deleteItem?.title}" ni o'chirishni tasdiqlaysizmi? Bu amal qaytarib bo'lmaydi.`}
        onConfirm={handleConfirmDelete}
        onCancel={() => {
          setIsConfirmOpen(false);
          setDeleteItem(null);
        }}
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
}
