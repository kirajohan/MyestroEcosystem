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
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || 'Tahrirlashda xatolik');
      }
      return resp.json() as Promise<ContentItem>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] });
    },
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
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || "O'chirishda xatolik");
      }
      return resp.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content'] });
    },
  });
}
