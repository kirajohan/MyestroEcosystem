"use client";

import { usePathname } from "next/navigation";
import Aurora from "./Aurora";

// Faqat shu yo'llarda Aurora ko'rinadi
const AURORA_PATHS = ["/", "/login", "/register"];

export function AuroraController() {
  const pathname = usePathname();

  // Aurora faqat landing va login sahifalarida
  const shouldShow = AURORA_PATHS.some((path) => pathname === path);

  if (!shouldShow) return null;

  return (
    <div className="fixed inset-0 z-0 pointer-events-none">
      <Aurora />
    </div>
  );
}