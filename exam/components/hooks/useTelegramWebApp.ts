"use client";

import { useEffect, useState } from "react";

interface TelegramWebApp {
  ready: () => void;
  expand: () => void;
  initData: string;
  initDataUnsafe: {
    user?: {
      id: number;
      first_name: string;
      last_name?: string;
      username?: string;
      photo_url?: string;
    };
  };
  themeParams: Record<string, string>;
  colorScheme: "light" | "dark";
}

export function useTelegramWebApp() {
  const [tg, setTg] = useState<TelegramWebApp | null>(null);
  const [isTelegram, setIsTelegram] = useState(false);

  useEffect(() => {
    const webapp = (window as any).Telegram?.WebApp;
    
    if (webapp) {
      webapp.ready();
      webapp.expand();
      setTg(webapp);
      setIsTelegram(true);
    }
  }, []);

  return { tg, isTelegram, initData: tg?.initData || "" };
}