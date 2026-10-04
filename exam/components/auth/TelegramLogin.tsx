"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { useLanguage } from "@/app/providers";

export interface TelegramAuthData {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

interface TelegramLoginProps {
  botUsername: string;
  onSuccess: (data: TelegramAuthData) => void;
  buttonSize?: "large" | "medium" | "small";
  cornerRadius?: number;
  requestAccess?: "write" | "read";
  userpic?: boolean;
}

export default function TelegramLogin({
  botUsername,
  onSuccess,
  buttonSize = "large",
  cornerRadius = 12,
  requestAccess = "write",
  userpic = true,
}: TelegramLoginProps) {
  const { lang, t } = useLanguage();
  const containerRef = useRef<HTMLDivElement>(null);
  const callbackRef = useRef(onSuccess);
  const [widgetReady, setWidgetReady] = useState(false);
  const [widgetError, setWidgetError] = useState(false);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    callbackRef.current = onSuccess;
  }, [onSuccess]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const callbackName = "onTelegramAuthCallback";
    (window as any)[callbackName] = (user: TelegramAuthData) => {
      callbackRef.current(user);
    };

    setWidgetReady(false);
    setWidgetError(false);
    container.innerHTML = "";

    // Telegram vidjeti o'zbek tilini qo'llamaydi — uz uchun inglizcha ko'rsatiladi
    const widgetLang = lang === "ru" ? "ru" : "en";

    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.setAttribute("data-telegram-login", botUsername);
    script.setAttribute("data-size", buttonSize);
    script.setAttribute("data-radius", String(cornerRadius));
    script.setAttribute("data-userpic", userpic ? "true" : "false");
    script.setAttribute("data-request-access", requestAccess);
    script.setAttribute("data-lang", widgetLang);
    script.setAttribute("data-onauth", `${callbackName}(user)`);
    script.async = true;
    script.onload = () => setWidgetReady(true);
    script.onerror = () => setWidgetError(true);
    container.appendChild(script);

    // 8 soniyada yuklanmasa — zaxira tugma ko'rsatiladi
    const timeout = setTimeout(() => {
      setWidgetReady((ready) => {
        if (!ready) setWidgetError(true);
        return ready;
      });
    }, 8000);

    return () => {
      clearTimeout(timeout);
      delete (window as any)[callbackName];
      container.innerHTML = "";
    };
  }, [botUsername, buttonSize, cornerRadius, requestAccess, userpic, lang, attempt]);

  return (
    <div className="w-full flex flex-col items-center gap-2">
      {/* Vidjet shu konteynerga qo'shiladi (har doim DOM'da turadi) */}
      <div ref={containerRef} className="flex justify-center" />

      {!widgetReady && (
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setAttempt((n) => n + 1)}
          disabled={!widgetError}
          className="w-full bg-[#0088cc] hover:bg-[#0077b3] text-white font-semibold py-3.5 rounded-xl flex items-center justify-center gap-3 shadow-lg transition-colors disabled:opacity-80"
          style={{ borderRadius: `${cornerRadius}px` }}
        >
          <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="currentColor"
          className="flex-shrink-0"
        >
          <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161c-.18 1.897-.962 6.502-1.359 8.627-.168.9-.5 1.201-.82 1.23-.697.064-1.226-.461-1.901-.903-1.056-.692-1.653-1.123-2.678-1.799-1.185-.781-.417-1.21.258-1.911.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.244-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.831-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635.099-.002.321.023.465.141.12.098.153.229.168.327.015.098.034.319.019.491z" />
        </svg>
          <span>
            {widgetError ? t("login.tg_retry") : t("common.loading")}
          </span>
        </motion.button>
      )}
    </div>
  );
}
