import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { StatsResponse, ActivityPoint, CEFRDistribution } from '@/lib/types';

export function useStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const response = await api.get<StatsResponse>('/stats');
      return response.data;
    },
    staleTime: 30000,
  });
}

export function useActivity() {
  return useQuery({
    queryKey: ['activity'],
    queryFn: async () => {
      const response = await api.get<ActivityPoint[]>('/stats/activity?days=7');
      return response.data;
    },
    staleTime: 30000,
  });
}

export function useCEFR() {
  return useQuery({
    queryKey: ['cefr'],
    queryFn: async () => {
      const response = await api.get<CEFRDistribution>('/stats/cefr');
      return response.data;
    },
    staleTime: 30000,
  });
}
