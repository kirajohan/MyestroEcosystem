import type { Metadata } from "next";
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

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="uz" suppressHydrationWarning>
      <head>
        {/* Preload font */}
        <script src="https://telegram.org/js/telegram-web-app.js" />
      </head>
      <body className="antialiased relative min-h-screen">
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