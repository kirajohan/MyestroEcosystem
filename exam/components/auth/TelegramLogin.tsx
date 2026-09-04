"use client";

import { useEffect, useRef } from "react";

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

  // Callback'ni har doim yangilab turadi
  useEffect(() => {
    callbackRef.current = onSuccess;
  }, [onSuccess]);

  useEffect(() => {
    // Global callback o'rnatish
    const callbackName = "onTelegramAuthCallback";
    (window as any)[callbackName] = (user: TelegramAuthData) => {
      callbackRef.current(user);
    };

    // Avvalgi script'ni tozalash
    if (containerRef.current) {
      containerRef.current.innerHTML = "";
    }

    // Telegram widget script'ni yaratish
    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.setAttribute("data-telegram-login", botUsername);
    script.setAttribute("data-size", buttonSize);
    script.setAttribute("data-radius", String(cornerRadius));
    script.setAttribute("data-userpic", userpic ? "true" : "false");
    script.setAttribute("data-request-access", requestAccess);
    script.setAttribute("data-onauth", `${callbackName}(user)`);
    script.async = true;

    if (containerRef.current) {
      containerRef.current.appendChild(script);
    }

    return () => {
      delete (window as any)[callbackName];
    };
  }, [botUsername, buttonSize, cornerRadius, requestAccess, userpic]);

  return <div ref={containerRef} className="flex justify-center" />;
}