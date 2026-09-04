"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

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
  const containerRef = useRef<HTMLDivElement>(null);
  const callbackRef = useRef(onSuccess);
  const [widgetLoaded, setWidgetLoaded] = useState(false);
  const [widgetError, setWidgetError] = useState(false);

  useEffect(() => {
    callbackRef.current = onSuccess;
  }, [onSuccess]);

  useEffect(() => {
    const callbackName = "onTelegramAuthCallback";
    
    (window as any)[callbackName] = (user: TelegramAuthData) => {
      callbackRef.current(user);
    };

    if (containerRef.current) {
      containerRef.current.innerHTML = "";
    }

    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.setAttribute("data-telegram-login", botUsername);
    script.setAttribute("data-size", buttonSize);
    script.setAttribute("data-radius", String(cornerRadius));
    script.setAttribute("data-userpic", userpic ? "true" : "false");
    script.setAttribute("data-request-access", requestAccess);
    script.setAttribute("data-onauth", `${callbackName}(user)`);
    script.async = true;

    script.onload = () => {
      setWidgetLoaded(true);
    };

    script.onerror = () => {
      setWidgetError(true);
    };

    // Timeout: agar 5 sekund ichida yuklanmasa, xato deb hisoblaymiz
    const timeout = setTimeout(() => {
      if (!widgetLoaded) {
        setWidgetError(true);
      }
    }, 5000);

    if (containerRef.current) {
      containerRef.current.appendChild(script);
    }

    return () => {
      clearTimeout(timeout);
      delete (window as any)[callbackName];
    };
  }, [botUsername, buttonSize, cornerRadius, requestAccess, userpic, widgetLoaded]);

  // Fallback button (agar widget yuklanmasa yoki xato bo'lsa)
  if (widgetError || !widgetLoaded) {
    return (
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => {
          // Widget'ni qayta yuklashga harakat qilish
          setWidgetError(false);
          setWidgetLoaded(false);
        }}
        className="w-full bg-[#0088cc] hover:bg-[#0077b3] text-white font-semibold py-3.5 rounded-xl flex items-center justify-center gap-3 shadow-lg transition-colors"
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
          {widgetError ? "Login with Telegram (qayta urinish)" : "Yuklanmoqda..."}
        </span>
      </motion.button>
    );
  }

  return <div ref={containerRef} className="flex justify-center" />;
}