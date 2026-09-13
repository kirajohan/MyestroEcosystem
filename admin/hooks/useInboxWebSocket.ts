import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/context/AuthContext';
import toast from 'react-hot-toast';

// ✅ JWT expire bo'lganini tekshirish
function isTokenExpired(token: string | null): boolean {
  if (!token) return true;
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(base64));
    // 5 sekund oldin expire bo'lsa ham yangi deb hisoblaymiz
    return typeof payload.exp === 'number' && payload.exp * 1000 < Date.now() + 5000;
  } catch {
    return true;
  }
}

export function useInboxWebSocket(onNewMessage?: () => void) {
  const { token, refreshToken, logout } = useAuth();
  const queryClient = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const onNewMessageRef = useRef(onNewMessage);
  onNewMessageRef.current = onNewMessage;

  useEffect(() => {
    if (!token) return;

    let stopped = false;       // effect cleanup belgisi
    let authFailed = false;    // auth xatosi belgisi

    const connect = async () => {
      if (stopped) return;

      // ✅ 1-QADAM: Token eskirgan bo'lsa, ULANISHDAN OLDIN refresh qilamiz
      let activeToken = token;
      if (isTokenExpired(token)) {
        console.log('🔄 WS: token eskirgan, avval refresh qilinmoqda...');
        const newToken = await refreshToken();
        if (!newToken) {
          console.error('❌ WS: refresh muvaffaqiyatsiz');
          return; // token state o'zgarmaydi → effect qayta urinmaydi, logout kerak
        }
        activeToken = newToken;
      }

      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8002';
      const ws = new WebSocket(`${wsUrl}/ws/admin`);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        ws.send(JSON.stringify({ token: activeToken }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // ✅ 2-QADAM: Auth xatosi kelsa — eski token bilan qayta urinmaymiz!
          if (data.type === 'error') {
            console.warn('⚠️ WS auth xatosi:', data.message);
            authFailed = true;
            ws.close();
            // Refresh qilamiz → token state yangilanadi → effect qayta ishga tushadi
            refreshToken().then((newToken) => {
              if (!newToken) {
                console.error('❌ WS: refresh failed, logout');
                logout();
              }
            });
            return;
          }

          if (data.type === 'pong') return;

          if (data.type === 'inbox_update') {
            console.log('📨 Inbox update:', data.event, data.data);
            queryClient.invalidateQueries({ queryKey: ['inbox-messages'] });

            if (onNewMessageRef.current) {
              onNewMessageRef.current();
            }

            if (data.event === 'new_message') {
              const userName = data.data?.user_name || 'Foydalanuvchi';
              const preview = data.data?.text?.substring(0, 50) || 'Yangi xabar';
              toast.success(`📩 ${userName}: ${preview}`, {
                duration: 4000,
                position: 'top-right',
              });
            }
          }
        } catch (error) {
          console.error('WebSocket message parse error:', error);
        }
      };

      ws.onclose = () => {
        if (stopped) return;
        // ✅ Auth xatosi bo'lsa — reconnect loop QILMAYMIZ (effect token bilan qayta ulaydi)
        if (authFailed) {
          console.log('⏳ WS: auth xatosi, token yangilanishi kutilmoqda...');
          return;
        }
        console.log('❌ WebSocket disconnected, reconnecting in 3s...');
        reconnectTimeoutRef.current = setTimeout(connect, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws.close();
      };
    };

    connect();

    return () => {
      stopped = true;
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [token, queryClient, refreshToken, logout]);
}