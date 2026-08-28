import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Maestro Exam",
  description: "Myestro — English Exam Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uz">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        {children}
      </body>
    </html>
  );
}