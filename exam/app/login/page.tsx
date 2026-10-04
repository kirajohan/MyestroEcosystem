"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import TelegramLogin from "@/components/auth/TelegramLogin";
import { setSessionToken } from "@/lib/session";
import { useLanguage } from "@/app/providers";
import AppTopBar from "@/components/AppTopBar";

const TELEGRAM_BOT_URL =
  process.env.NEXT_PUBLIC_TELEGRAM_BOT_URL || "https://t.me/myestro_uz_bot";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://myestroeco-backend-production.up.railway.app";
const BOT_USERNAME =
  process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME || "MyestroEcoBot";

export default function LoginPage() {
  const { t } = useLanguage();
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ═══ Sessiyani saqlash (localStorage + middleware uchun cookie) ═══
  function persistSession(accessToken: string) {
    setSessionToken(accessToken);
    const isSecure = window.location.protocol === "https:";
    const cookieParts = [
      `maestro_session=${accessToken}`,
      "path=/",
      "max-age=604800", // 7 kun
      "SameSite=Lax",
    ];
    if (isSecure) cookieParts.push("Secure");
    document.cookie = cookieParts.join("; ");
  }

  function redirectTarget() {
    const redirect = new URLSearchParams(window.location.search).get("redirect");
    // Faqat ichki yo'llarga ruxsat (open redirect'dan himoya)
    return redirect && redirect.startsWith("/") && !redirect.startsWith("//")
      ? redirect
      : "/cabinet";
  }

  // ═══ Telegram Login Widget callback ═══
  async function handleTelegramAuth(telegramData: any) {
    setError("");
    try {
      const res = await fetch(`${API_URL}/api/v2/exam/auth/telegram/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(telegramData),
      });
      if (!res.ok) throw new Error(t("login.err_login"));
      const { access_token } = await res.json();
      persistSession(access_token);
      window.location.href = redirectTarget();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("login.err_failed"));
    }
  }

  // ═══ Bot'ga yo'naltirish (ro'yxatdan o'tish) ═══
  const goToTelegramBot = () => {
    window.location.href = TELEGRAM_BOT_URL;
  };

// ═══ Phone + Password login ═══
async function handlePhoneLogin(e: React.FormEvent) {
  e.preventDefault();
  setError("");
  setLoading(true);

  try {
    const res = await fetch(`${API_URL}/api/v2/exam/auth/login`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone, password }),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || t("login.err_login"));
    }

    const { access_token } = await res.json();
    persistSession(access_token);
    window.location.href = redirectTarget();
  } catch (err) {
    setError(err instanceof Error ? err.message : t("login.err_failed"));
  } finally {
    setLoading(false);
  }
}

  return (
    <main className="min-h-screen flex bg-gradient-to-br from-orange-50 via-white to-rose-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 relative overflow-hidden">
      {/* Background floating shapes */}
      <motion.div
        className="absolute top-20 left-20 w-64 h-64 bg-orange-300/30 rounded-full blur-3xl"
        animate={{ x: [0, 50, 0], y: [0, 30, 0] }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute bottom-20 right-20 w-96 h-96 bg-rose-300/30 rounded-full blur-3xl"
        animate={{ x: [0, -50, 0], y: [0, -30, 0] }}
        transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
      />

      <AppTopBar className="absolute top-4 right-4 z-20" />

      {/* Left — Brand Side */}
      <div className="hidden lg:flex lg:w-1/2 relative items-center justify-center p-12">
        <div className="max-w-md relative z-10">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex items-center gap-3 mb-8">
              <Image
                src="/logo.png"
                alt="Maestro Exam"
                width={48}
                height={48}
                className="rounded-xl"
              />
              <span className="text-2xl font-bold text-slate-900 dark:text-white">Maestro Exam</span>
            </div>
            <h1 className="text-5xl font-bold text-slate-900 dark:text-white mb-6 leading-tight">
              {t("login.brand_title_1")}
              <br />
              <span className="bg-gradient-to-r from-orange-600 to-rose-500 bg-clip-text text-transparent">
                {t("login.brand_title_2")}
              </span>
            </h1>
            <p className="text-lg text-slate-600 dark:text-slate-300 mb-8">
              {t("login.brand_text")}
            </p>
            <div className="space-y-3">
              {[t("login.brand_f1"), t("login.brand_f2"), t("login.brand_f3")].map((item, i) => (
                <motion.div
                  key={item}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + i * 0.1 }}
                  className="flex items-center gap-3"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-500 to-rose-500 flex items-center justify-center text-white">
                    ✓
                  </div>
                  <span className="text-slate-700 dark:text-slate-200">{item}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Right — Form Side */}
      <div className="flex-1 flex items-center justify-center p-6 relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          {/* Logo on mobile */}
          <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
            <Image
              src="/logo.png"
              alt="Maestro Exam"
              width={40}
              height={40}
              className="rounded-lg"
            />
            <span className="text-xl font-bold text-slate-900 dark:text-white">Maestro Exam</span>
          </div>

          {/* Card */}
          <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/50 dark:border-slate-700/50">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2 text-center">
              {t("login.welcome")}
            </h2>
            <p className="text-slate-500 dark:text-slate-400 text-center mb-8">
              {t("login.subtitle")}
            </p>

            {/* Error message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-4 bg-red-50 border border-red-200 text-red-700 dark:bg-red-950/50 dark:border-red-900 dark:text-red-300 p-3 rounded-xl text-sm flex items-center gap-2"
              >
                <span>❌</span>
                <span>{error}</span>
              </motion.div>
            )}

            {/* ═══ TELEGRAM LOGIN WIDGET ═══ */}
            <div className="mb-4">
              <div className="flex items-center justify-center min-h-[52px]">
                <TelegramLogin
                  botUsername={BOT_USERNAME}
                  onSuccess={handleTelegramAuth}
                  buttonSize="large"
                  cornerRadius={12}
                />
              </div>
            </div>

            {/* ═══ BOT ORQALI RO'YXATDAN O'TISH (YASHIL CTA) ═══ */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={goToTelegramBot}
              className="w-full bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white font-semibold py-3.5 rounded-xl flex items-center justify-center gap-3 shadow-lg transition-all"
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
              <span>{t("login.bot_register")}</span>
            </motion.button>

            {/* Info box */}
            <div className="mt-3 bg-emerald-50 border border-emerald-100 dark:bg-emerald-950/40 dark:border-emerald-900 rounded-xl p-2.5 text-[11px] text-emerald-700 dark:text-emerald-300 text-center">
              {t("login.bot_info")}
            </div>

            {/* ═══ DIVIDER ═══ */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200 dark:border-slate-700" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white dark:bg-slate-900 text-slate-400">
                  {t("login.divider")}
                </span>
              </div>
            </div>

            {/* ═══ PHONE + PASSWORD FORM ═══ */}
            <form className="space-y-4" onSubmit={handlePhoneLogin}>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                  {t("login.phone")}
                </label>
                <input
                  type="tel"
                  placeholder="+998 90 123 45 67"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  required
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white focus:border-orange-500 focus:ring-2 focus:ring-orange-200 outline-none transition"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                  {t("login.password")}
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white focus:border-orange-500 focus:ring-2 focus:ring-orange-200 outline-none transition"
                />
              </div>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={loading}
                className={`w-full font-semibold py-3.5 rounded-xl shadow-lg transition-colors ${
                  loading
                    ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                    : "bg-gradient-to-r from-orange-600 to-rose-500 hover:from-orange-700 hover:to-rose-600 text-white"
                }`}
              >
                {loading ? t("common.loading") : t("login.submit")}
              </motion.button>
            </form>

            {/* Bottom link */}
            <p className="text-center text-sm text-slate-600 dark:text-slate-400 mt-6">
              {t("login.no_account")}{" "}
              <button
                onClick={goToTelegramBot}
                className="text-orange-600 hover:text-orange-700 font-semibold"
              >
                {t("login.go_bot")}
              </button>
            </p>
          </div>

          {/* Back to home */}
          <div className="text-center mt-6">
            <Link
              href="/"
              className="text-sm text-slate-500 dark:text-slate-400 hover:text-orange-600"
            >
              {t("common.back_home")}
            </Link>
          </div>
        </motion.div>
      </div>
    </main>
  );
}