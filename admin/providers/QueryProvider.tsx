'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState, ReactNode } from 'react';

interface QueryProviderProps {
  children: ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 daqiqa (ma'lumotlar qancha vaqt "yangi" hisoblanadi)
            gcTime: 5 * 60 * 1000, // 5 daqiqa (eski ma'lumotlar qachon o'chiriladi)
            retry: 1, // Xatolik bo'lsa 1 marta qayta urinadi
            refetchOnWindowFocus: false, // Oyna fokusga kelganda qayta yuklamaslik
          },
          mutations: {
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* Faqat development rejimida devtools ko'rinadi */}
      {process.env.NODE_ENV === 'development' && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
}