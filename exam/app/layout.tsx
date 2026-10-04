import type { Metadata, Viewport } from "next";
import Script from "next/script";
import "./globals.css";
import { ThemeProvider, LanguageProvider } from "./providers";
import { AuroraController } from "@/components/landing/AuroraController";

export const metadata: Metadata = {
  title: "Maestro Exam — Ingliz tili imtihonlari",
  description:
    "Listening, Reading, Writing va Speaking bo'yicha onlayn imtihonlar. AI baholash bilan darajangizni aniqlang.",
  keywords: ["ingliz tili", "imtihon", "CEFR", "IELTS"],
  icons: { icon: "/favicon.ico" },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

// Tema class'ini birinchi paintdan oldin qo'yadi (chaqnashsiz).
// localStorage bloklangan bo'lsa (private mode, in-app brauzerlar) jimgina o'tib ketadi.
const themeInitScript = `(function(){try{var t=null;try{t=localStorage.getItem("theme")}catch(e){}if(t==="dark"||(t!=="light"&&window.matchMedia&&window.matchMedia("(prefers-color-scheme: dark)").matches)){document.documentElement.classList.add("dark")}}catch(e){}})();`;

// <html lang> ni birinchi paintdan oldin saqlangan tilga moslaydi.
const langInitScript = `(function(){try{var l=localStorage.getItem("lang");if(l==="uz"||l==="ru"||l==="en"){document.documentElement.lang=l}}catch(e){}})();`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="uz" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
        <script dangerouslySetInnerHTML={{ __html: langInitScript }} />
      </head>
      <body className="antialiased relative min-h-screen min-h-[100dvh]">
        {/* Bloklamaydi: sahifa chizilgandan keyin yuklanadi */}
        <Script
          src="https://telegram.org/js/telegram-web-app.js"
          strategy="lazyOnload"
        />
        <ThemeProvider>
          <LanguageProvider>
            {/* Global Aurora — faqat public sahifalarda */}
            <AuroraController />
            {children}
          </LanguageProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
