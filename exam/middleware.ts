import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const SESSION_COOKIE = "maestro_session";

// Auth talab qilinmaydigan yo'llar (public)
const PUBLIC_PATHS = [
  "/",              // Landing page
  "/login",         // Login sahifasi
  "/register",      // Ro'yxatdan o'tish (agar bor bo'lsa)
];

export function middleware(request: NextRequest) {
  const session = request.cookies.get(SESSION_COOKIE);
  const path = request.nextUrl.pathname;

  // Static fayllar (har doim ruxsat)
  if (
    path.startsWith("/_next") ||
    path.startsWith("/favicon") ||
    path.includes(".") // .png, .svg, .ico, va hokazo
  ) {
    return NextResponse.next();
  }

  // Public yo'llar
  const isPublicPath = PUBLIC_PATHS.includes(path);

  // Session bor va public sahifada → cabinet'ga yo'naltirish
  if (session && isPublicPath) {
    return NextResponse.redirect(new URL("/cabinet", request.url));
  }

  // Session yo'q va protected sahifada → login'ga yo'naltirish
  if (!session && !isPublicPath) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Qolgan holatlar → davom etish
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)"],
};