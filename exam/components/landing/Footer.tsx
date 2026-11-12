"use client";

import Link from "next/link";
import Image from "next/image";
import { useTheme, useLanguage } from "@/app/providers";

const SOCIAL_LINKS = [
  {
    name: "Telegram",
    href: "https://t.me/myestro_community",
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161c-.18 1.897-.962 6.502-1.359 8.627-.168.9-.5 1.201-.82 1.23-.697.064-1.226-.461-1.901-.903-1.056-.692-1.653-1.123-2.678-1.799-1.185-.781-.417-1.21.258-1.911.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.244-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.831-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635.099-.002.321.023.465.141.12.098.153.229.168.327.015.098.034.319.019.491z"/>
      </svg>
    ),
  },
  {
    name: "Instagram",
    href: "https://instagram.com/myestro_edu",
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
      </svg>
    ),
  },
  {
    name: "YouTube",
    href: "https://youtube.com/@myestro_edu",
    icon: (
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
      </svg>
    ),
  },
];

const LEGAL_LINKS = [
  { key: "footer.offer", href: "/offerta" },
  { key: "footer.privacy", href: "/privacy" },
  { key: "footer.terms", href: "/terms" },
  { key: "footer.docs_link", href: "/docs" },
];

const NAV_SECTIONS = [
  { id: "features", key: "nav_features" },
  { id: "method", key: "nav_method" },
  { id: "results", key: "nav_results" },
  { id: "faq", key: "nav_faq" },
];

export default function Footer() {
  const { theme } = useTheme();
  const { t } = useLanguage();
  const isDark = theme === "dark";

  return (
    <footer
      className={`border-t transition-colors ${
        isDark ? "bg-slate-950 border-slate-800" : "bg-slate-50 border-slate-200"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 py-14">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10 mb-10">
          {/* Brand */}
          <div className="lg:col-span-1">
            <div className="flex items-center gap-3 mb-4">
              <Image src="/logo.png" alt="Maestro" width={40} height={40} className="rounded-lg" />
              <span className={`text-xl font-bold ${isDark ? "text-white" : "text-slate-900"}`}>
                Maestro Exam
              </span>
            </div>
            <p className={`text-sm leading-relaxed ${isDark ? "text-slate-400" : "text-slate-600"}`}>
              {t("footer.desc")}
            </p>
          </div>

          {/* Navigation */}
          <div>
            <h4 className={`font-semibold mb-4 ${isDark ? "text-white" : "text-slate-900"}`}>
              {t("footer.pages")}
            </h4>
            <ul className="space-y-2.5">
              {NAV_SECTIONS.map((section) => (
                <li key={section.id}>
                  <a
                    href={`#${section.id}`}
                    className={`text-sm transition-colors ${
                      isDark ? "text-slate-400 hover:text-orange-400" : "text-slate-600 hover:text-orange-600"
                    }`}
                  >
                    {t(section.key)}
                  </a>
                </li>
              ))}
              <li>
                <Link
                  href="/login"
                  className={`text-sm transition-colors ${
                    isDark ? "text-slate-400 hover:text-orange-400" : "text-slate-600 hover:text-orange-600"
                  }`}
                >
                  {t("nav_login")}
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className={`font-semibold mb-4 ${isDark ? "text-white" : "text-slate-900"}`}>
              {t("footer.docs")}
            </h4>
            <ul className="space-y-2.5">
              {LEGAL_LINKS.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className={`text-sm transition-colors ${
                      isDark ? "text-slate-400 hover:text-orange-400" : "text-slate-600 hover:text-orange-600"
                    }`}
                  >
                    {t(link.key)}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact + Admin */}
          <div>
            <h4 className={`font-semibold mb-4 ${isDark ? "text-white" : "text-slate-900"}`}>
              {t("footer.contact")}
            </h4>
            <ul className="space-y-2.5">
              <li>
                <a
                  href="https://t.me/myestro_support"
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`text-sm transition-colors ${
                    isDark ? "text-slate-400 hover:text-orange-400" : "text-slate-600 hover:text-orange-600"
                  }`}
                >
                  {t("footer.admin_contact")}
                </a>
              </li>
              <li>
                <a
                  href="mailto:support@myestro.uz"
                  className={`text-sm transition-colors ${
                    isDark ? "text-slate-400 hover:text-orange-400" : "text-slate-600 hover:text-orange-600"
                  }`}
                >
                  ✉️ support@myestro.uz
                </a>
              </li>
            </ul>

            <div className="mt-6">
              <Link
                href="/admin"
                target="_blank"
                className={`inline-flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                  isDark
                    ? "border-slate-800 text-slate-500 hover:text-slate-300 hover:border-slate-700"
                    : "border-slate-200 text-slate-400 hover:text-slate-600 hover:border-slate-300"
                }`}
              >
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                {t("footer.admin_panel")}
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div
          className={`pt-8 border-t flex flex-col md:flex-row items-center justify-between gap-4 ${
            isDark ? "border-slate-800" : "border-slate-200"
          }`}
        >
          <p className={`text-sm ${isDark ? "text-slate-500" : "text-slate-500"}`}>
            {t("footer.rights")}
          </p>

          <div className="flex items-center gap-2">
            {SOCIAL_LINKS.map((social) => (
              <a
                key={social.name}
                href={social.href}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={social.name}
                className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all ${
                  isDark
                    ? "text-slate-400 hover:text-orange-400 hover:bg-slate-800"
                    : "text-slate-600 hover:text-orange-600 hover:bg-white hover:shadow-md"
                }`}
              >
                {social.icon}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}