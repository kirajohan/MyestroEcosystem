import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { UserResponse, UserUpdate, SendMessageRequest, SendMessageResponse } from '@/lib/types';

interface UsersListParams {
  skip: number;
  limit: number;
}

interface UsersListResponse {
  data: UserResponse[];
  total: number;
}

export function useUsers(params: UsersListParams) {
  return useQuery({
    queryKey: ['users', params.skip, params.limit],
    queryFn: async () => {
      const response = await api.get<UsersListResponse>('/users', {
        params: {
          skip: params.skip,
          limit: params.limit,
        },
      });
      return response.data;
    },
    staleTime: 30000,
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: UserUpdate }) => {
      const response = await api.put<UserResponse>(`/users/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/users/${id}`);
    },
    onSuccess: () => {
      // Barcha 'users' bilan bog'liq queries ni invalidate qil
      queryClient.invalidateQueries({ queryKey: ['users'], exact: false });
    },
  });
}

export function useSendMessage() {
  return useMutation({
    mutationFn: async (data: SendMessageRequest) => {
      const response = await api.post<SendMessageResponse>('/admin/send-message', data);
      return response.data;
    },
  });
}
