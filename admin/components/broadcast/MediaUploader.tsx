// components/broadcast/MediaUploader.tsx
"use client";

import { authFetch } from '@/lib/auth';
import { useState, useRef, useCallback } from "react";

interface UploadedFile {
  filename: string;
  content_type: string;
  file_id: string;
  telegram_file_id?: string;
}

interface MediaUploaderProps {
  onUploadComplete: (files: UploadedFile[]) => void;
  uploadedFiles: UploadedFile[];
  onRemove: (index: number) => void;
}

export default function MediaUploader({ onUploadComplete, uploadedFiles, onRemove }: MediaUploaderProps) {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const uploadFiles = useCallback(async (files: FileList | File[]) => {
    const fileArray = Array.from(files);
    if (fileArray.length === 0) return;

    setUploading(true);
    setProgress(0);

    const completed: UploadedFile[] = [];

    for (let i = 0; i < fileArray.length; i++) {
      const file = fileArray[i];
      const formData = new FormData();
      formData.append("file", file);

      try {
        const res = await authFetch("/api/broadcast/upload", {
          method: "POST",
          body: formData,
        });

        if (!res.ok) {
          const err = await res.json();
          console.error(`Upload failed for ${file.name}:`, err);
          continue;
        }

        const data = await res.json();

        // Backend now returns telegram_file_id immediately (synchronous upload)
        // Use telegram_file_id as the primary file_id; fall back to upload_id
        const tgFileId = data.telegram_file_id || data.upload_id;

        if (!tgFileId || data.status !== "completed") {
          console.error(`Upload incomplete for ${file.name}: status=${data.status}, telegram_file_id=${tgFileId}`);
          continue;
        }

        completed.push({
          filename: data.filename || file.name,
          content_type: data.content_type || file.type,
          file_id: tgFileId,
          telegram_file_id: tgFileId,
        });
      } catch (e) {
        console.error(`Upload error for ${file.name}:`, e);
      }

      setProgress(Math.round(((i + 1) / fileArray.length) * 100));
    }

    onUploadComplete(completed);
    setUploading(false);
    setProgress(0);
  }, [onUploadComplete]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      uploadFiles(e.dataTransfer.files);
    }
  }, [uploadFiles]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadFiles(e.target.files);
    }
  }, [uploadFiles]);

  return (
    <div className="space-y-3">
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`cursor-pointer rounded-lg border-2 border-dashed p-6 text-center transition-colors ${
          dragOver
            ? "border-primary bg-primary-50"
            : "border-gray-300 hover:border-primary"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,video/*,.pdf,.doc,.docx,.xls,.xlsx,.txt"
          onChange={handleFileSelect}
          className="hidden"
        />
        <div className="text-sm text-gray-500">
          <span className="font-medium text-primary">Fayl tanlash</span> yoki drag&drop
        </div>
        <p className="mt-1 text-xs text-gray-400">
          Rasm, video yoki hujjat (max 50MB)
        </p>
      </div>

      {/* Upload progress */}
      {uploading && (
        <div className="space-y-1">
          <div className="flex justify-between text-xs text-gray-500">
            <span>Yuklanmoqda...</span>
            <span>{progress}%</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full bg-primary transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Uploaded files list */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-1.5">
          {uploadedFiles.map((file, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between rounded border border-gray-200 bg-gray-50 px-3 py-2"
            >
              <div className="flex items-center gap-2 text-xs">
                <span className="text-gray-400">
                  {file.content_type.startsWith("image/") ? "🖼" : file.content_type.startsWith("video/") ? "🎬" : "📄"}
                </span>
                <span className="text-gray-700">{file.filename}</span>
                {file.telegram_file_id && (
                  <span className="rounded bg-emerald-100 px-1.5 py-0.5 text-[10px] text-emerald-700">
                    Telegram&#39;da
                  </span>
                )}
              </div>
              <button
                onClick={() => onRemove(idx)}
                className="text-xs text-rose-500 hover:text-rose-700"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}