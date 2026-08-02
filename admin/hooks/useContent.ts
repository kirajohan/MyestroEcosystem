import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ContentItem } from '@/lib/types';

// GET /api/content — barcha content ro'yxati
export function useContentList() {
  return useQuery({
    queryKey: ['content'],
    queryFn: async () => {
      const resp = await fetch('/api/content');
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || 'Contentni olishda xatolik');
      }
      return resp.json() as Promise<ContentItem[]>;
    },
    staleTime: 30000,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

// POST /api/content — yangi content yuklash (FormData orqali)
// Next.js API proxy orqali backend'ga yuboriladi (admin/app/api/content/route.ts)
export function useCreateContent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (formData: FormData) => {
      const resp = await fetch('/api/content', {
        method: 'POST',
        body: formData,
      });
      
      if (!resp.ok) {
        let errorMessage = 'Yuklashda xatolik';
        try {
          const err = await resp.json();
          errorMessage = err.detail || errorMessage;
        } catch {
          const errText = await resp.text();
          errorMessage = errText || errorMessage;
        }
        throw new Error(errorMessage);
      }
      
      return resp.json() as Promise<ContentItem>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] });
    },
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(2000 * 2 ** attemptIndex, 10000),
  });
}

// PATCH /api/contents/[id] — tahrirlash (matn + ixtiyoriy fayl)
export function useUpdateContent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, formData }: { id: number; formData: FormData }) => {
      const resp = await fetch(`/api/contents/${id}`, {
        method: 'PATCH',
        body: formData,
      });
      
      if (!resp.ok) {
        let errorMessage = 'Tahrirlashda xatolik';
        try {
          const err = await resp.json();
          errorMessage = err.detail || errorMessage;
        } catch {
          const errText = await resp.text();
          errorMessage = errText || errorMessage;
        }
        throw new Error(errorMessage);
      }
      
      return resp.json() as Promise<ContentItem>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] });
    },
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(2000 * 2 ** attemptIndex, 10000),
  });
}

// DELETE /api/contents/[id] — o'chirish
export function useDeleteContent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const resp = await fetch(`/api/contents/${id}`, {
        method: 'DELETE',
      });
      
      if (!resp.ok) {
        let errorMessage = "O'chirishda xatolik";
        try {
          const err = await resp.json();
          errorMessage = err.detail || err.message || errorMessage;
        } catch {
          const errText = await resp.text();
          errorMessage = errText || errorMessage;
        }
        throw new Error(errorMessage);
      }
      
      return resp.json().catch(() => ({ message: 'Deleted' }));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] });
    },
    retry: 1,
    retryDelay: 1000,
  });
}
