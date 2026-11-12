'use client';

import { useState, FormEvent, ChangeEvent, useRef, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import {
  Video,
  FileText,
  Upload,
  CheckCircle,
  List,
  AlertCircle,
  RefreshCw,
  X,
  Search,
  File,
  Download,
  Trash2,
  Pencil,
  Eye,
  Clock,
  Filter,
} from 'lucide-react';
import { useContentList, useCreateContent, useUpdateContent, useDeleteContent } from '@/hooks/useContent';
import { ContentItem } from '@/lib/types';
import { ContentTable } from '@/components/content/ContentTable';
import { EditContentModal } from '@/components/content/EditContentModal';
import { ConfirmDialog } from '@/components/ui/ConfirmDialog';

export default function ContentPage() {
  // Upload form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [contentType, setContentType] = useState<'video' | 'file'>('video');
  const [file, setFile] = useState<File | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  // Table / modal / confirm state
  const [editItem, setEditItem] = useState<ContentItem | null>(null);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [deleteItem, setDeleteItem] = useState<ContentItem | null>(null);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);

  // Filter / search
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'video' | 'file'>('all');

  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: contents, isLoading: isListLoading, refetch: refetchContents } = useContentList();
  const createMutation = useCreateContent();
  const updateMutation = useUpdateContent();
  const deleteMutation = useDeleteContent();

  // Stats
  const stats = useMemo(() => {
    const items = contents || [];
    return {
      total: items.length,
      videos: items.filter((c) => c.content_type === 'video').length,
      files: items.filter((c) => c.content_type === 'file').length,
    };
  }, [contents]);

  // Filtered items
  const filteredContents = useMemo(() => {
    if (!contents) return [];
    let result = contents;

    if (filterType !== 'all') {
      result = result.filter((c) => c.content_type === filterType);
    }

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (c) =>
          c.title?.toLowerCase().includes(q) ||
          c.description?.toLowerCase().includes(q)
      );
    }

    return result;
  }, [contents, filterType, searchQuery]);

  // Upload handlers
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadSuccess(false);
      setUploadError(null);
    }
  };

  // Drag & drop
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (contentType === 'video' && !droppedFile.type.startsWith('video/')) {
        toast.error('Faqat video fayllar qabul qilinadi');
        return;
      }
      setFile(droppedFile);
      setUploadSuccess(false);
      setUploadError(null);
    }
  };

  const clearFile = () => {
    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
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
      const data = await createMutation.mutateAsync(formData);
      toast.success(`Muvaffaqiyatli yuklandi!`);
      setUploadSuccess(true);

      setTitle('');
      setDescription('');
      clearFile();
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
      await createMutation.mutateAsync(formData);
      toast.success('Qayta urinish muvaffaqiyatli!');
      setUploadSuccess(true);
      setUploadError(null);

      setTitle('');
      setDescription('');
      clearFile();
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
      toast.success('Ochirildi');
      setIsConfirmOpen(false);
      setDeleteItem(null);
    } catch (err: any) {
      toast.error(err.message || 'Ochirishda xatolik');
    }
  };

  // File size formatting
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Content boshqaruvi</h1>
          <p className="text-sm md:text-base text-slate-600 mt-1">
            Video va fayllarni Telegram kanaliga yuklang va boshqaring
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 md:gap-4">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl md:rounded-2xl border border-slate-200 p-4 md:p-5 shadow-sm"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="w-9 h-9 md:w-10 md:h-10 bg-slate-100 rounded-lg flex items-center justify-center">
              <List className="w-4 h-4 md:w-5 md:h-5 text-slate-600" />
            </div>
          </div>
          <p className="text-xl md:text-2xl font-bold text-slate-900">{stats.total}</p>
          <p className="text-xs text-slate-500 mt-1">Jami content</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="bg-white rounded-xl md:rounded-2xl border border-orange-100 p-4 md:p-5 shadow-sm"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="w-9 h-9 md:w-10 md:h-10 bg-orange-50 rounded-lg flex items-center justify-center">
              <Video className="w-4 h-4 md:w-5 md:h-5 text-orange-600" />
            </div>
          </div>
          <p className="text-xl md:text-2xl font-bold text-slate-900">{stats.videos}</p>
          <p className="text-xs text-slate-500 mt-1">Videolar</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl md:rounded-2xl border border-blue-100 p-4 md:p-5 shadow-sm"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="w-9 h-9 md:w-10 md:h-10 bg-blue-50 rounded-lg flex items-center justify-center">
              <File className="w-4 h-4 md:w-5 md:h-5 text-blue-600" />
            </div>
          </div>
          <p className="text-xl md:text-2xl font-bold text-slate-900">{stats.files}</p>
          <p className="text-xs text-slate-500 mt-1">Fayllar</p>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Form */}
        <div className="lg:col-span-1">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden lg:sticky lg:top-24"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-5">
              <div className="flex items-center gap-3 text-white">
                <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                  <Upload className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold">Yangi content</h2>
                  <p className="text-xs text-white/80">Yuklash va Telegram ga joylash</p>
                </div>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="p-5 space-y-5">
              {/* Type selector */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-2">
                  Turi
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setContentType('video');
                      clearFile();
                    }}
                    className={`flex flex-col items-center gap-2 p-3 rounded-xl border-2 transition-all ${
                      contentType === 'video'
                        ? 'border-orange-500 bg-orange-50'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <Video
                      size={20}
                      className={contentType === 'video' ? 'text-orange-600' : 'text-slate-400'}
                    />
                    <span
                      className={`text-xs font-medium ${
                        contentType === 'video' ? 'text-orange-700' : 'text-slate-600'
                      }`}
                    >
                      Video
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setContentType('file');
                      clearFile();
                    }}
                    className={`flex flex-col items-center gap-2 p-3 rounded-xl border-2 transition-all ${
                      contentType === 'file'
                        ? 'border-orange-500 bg-orange-50'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <FileText
                      size={20}
                      className={contentType === 'file' ? 'text-orange-600' : 'text-slate-400'}
                    />
                    <span
                      className={`text-xs font-medium ${
                        contentType === 'file' ? 'text-orange-700' : 'text-slate-600'
                      }`}
                    >
                      Fayl
                    </span>
                  </button>
                </div>
              </div>

              {/* Title */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-2">
                  Sarlavha <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="Masalan: Python 1-dars"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all text-sm"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-2">
                  Izoh
                </label>
                <textarea
                  placeholder="Dars haqida qisqa izoh..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  className="w-full px-4 py-2.5 border border-slate-200 rounded-xl bg-slate-50 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all text-sm resize-none"
                />
              </div>

              {/* File upload - drag & drop */}
              <div>
                <label className="block text-sm font-semibold text-slate-900 mb-2">
                  Fayl <span className="text-red-500">*</span>
                </label>

                {!file ? (
                  <label
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-all ${
                      isDragging
                        ? 'border-orange-500 bg-orange-50'
                        : 'border-slate-300 hover:border-orange-400 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex flex-col items-center gap-2 text-slate-500">
                      <Upload
                        size={24}
                        className={isDragging ? 'text-orange-500' : 'text-slate-400'}
                      />
                      <span className="text-xs text-center px-4">
                        {isDragging
                          ? 'Shu yerga qoying...'
                          : 'Faylni tanlang yoki shu yerga tashlang'}
                      </span>
                    </div>
                    <input
                      ref={fileInputRef}
                      type="file"
                      className="sr-only"
                      accept={contentType === 'video' ? 'video/*' : '*/*'}
                      onChange={handleFileChange}
                    />
                  </label>
                ) : (
                  <div className="flex items-center gap-3 p-3 bg-orange-50 border border-orange-200 rounded-xl">
                    <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      {contentType === 'video' ? (
                        <Video className="w-5 h-5 text-orange-600" />
                      ) : (
                        <File className="w-5 h-5 text-orange-600" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">{file.name}</p>
                      <p className="text-xs text-slate-500">{formatFileSize(file.size)}</p>
                    </div>
                    <button
                      type="button"
                      onClick={clearFile}
                      className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>

              {/* Success message */}
              <AnimatePresence>
                {uploadSuccess && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="flex items-center gap-2 p-3 bg-emerald-50 border border-emerald-200 rounded-xl"
                  >
                    <CheckCircle className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                    <span className="text-sm font-medium text-emerald-700">
                      Muvaffaqiyatli yuklandi!
                    </span>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Error message */}
              <AnimatePresence>
                {uploadError && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-xl"
                  >
                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-red-700">Yuklashda xatolik</p>
                      <p className="text-xs text-red-600 mt-0.5 break-words">{uploadError}</p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Action buttons */}
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={isUploading || !file || !title.trim()}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-xl font-semibold text-sm hover:from-orange-600 hover:to-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-orange-500/20"
                >
                  {isUploading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Yuklanmoqda...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      Yuklash
                    </>
                  )}
                </button>

                {uploadError && (
                  <button
                    type="button"
                    onClick={handleRetry}
                    disabled={isUploading}
                    className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-xl font-medium text-sm hover:bg-slate-50 disabled:opacity-50 transition"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                )}
              </div>
            </form>
          </motion.div>
        </div>

        {/* Content List */}
        <div className="lg:col-span-2">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden"
          >
            {/* Header */}
            <div className="p-5 border-b border-slate-100">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center">
                    <List className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-slate-900">
                      Saqlangan contentlar
                    </h2>
                    <p className="text-xs text-slate-500">{filteredContents.length} ta natija</p>
                  </div>
                </div>
              </div>

              {/* Search + Filter */}
              <div className="flex flex-col sm:flex-row gap-2">
                <div className="relative flex-1">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="Sarlavha boyicha qidirish..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-xl bg-slate-50 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all"
                  />
                </div>

                <div className="flex gap-1.5 bg-slate-100 p-1 rounded-xl">
                  {[
                    { label: 'Hammasi', value: 'all' },
                    { label: 'Video', value: 'video' },
                    { label: 'Fayl', value: 'file' },
                  ].map((f) => (
                    <button
                      key={f.value}
                      onClick={() => setFilterType(f.value as any)}
                      className={`flex-1 sm:flex-none px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                        filterType === f.value
                          ? 'bg-white text-orange-600 shadow-sm'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                    >
                      {f.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="p-0">
              {isListLoading ? (
                <div className="p-8 space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-slate-200 rounded-lg animate-pulse" />
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-slate-200 rounded animate-pulse w-3/4" />
                        <div className="h-3 bg-slate-100 rounded animate-pulse w-1/2" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : filteredContents.length === 0 ? (
                <div className="p-12 text-center">
                  <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <File className="w-8 h-8 text-slate-300" />
                  </div>
                  <h3 className="text-base font-semibold text-slate-900 mb-1">
                    Content topilmadi
                  </h3>
                  <p className="text-sm text-slate-500">
                    {searchQuery || filterType !== 'all'
                      ? 'Filter yoki qidiruv shartlariga mos content yoq'
                      : 'Hali hech qanday content yuklanmagan'}
                  </p>
                </div>
              ) : (
                <ContentTable
                  items={filteredContents}
                  isLoading={false}
                  onEdit={handleEdit}
                  onDelete={handleDeleteClick}
                />
              )}
            </div>
          </motion.div>
        </div>
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
        title="Contentni ochirish"
        message={`${deleteItem?.title} ni ochirishni tasdiqlaysizmi? Bu amal qaytarib bolmaydi.`}
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