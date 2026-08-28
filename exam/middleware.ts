// middleware.ts
// Session cookie bo'lmasa /login ga yo'naltiradi.

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const SESSION_COOKIE = "maestro_session";

export function middleware(request: NextRequest) {
  const session = request.cookies.get(SESSION_COOKIE);
  const path = request.nextUrl.pathname;

  const isLoginPage = path.startsWith("/login");
  const isPublic = path === "/" || path.startsWith("/_next") || path.startsWith("/favicon");

  if (isPublic) {
    return NextResponse.next();
  }

  // Sessiya yo'q va login sahifasida emas → login'ga yo'naltirish
  if (!session && !isLoginPage) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Sessiya bor va login sahifasida → cabinet'ga yo'naltirish
  if (session && isLoginPage) {
    return NextResponse.redirect(new URL("/cabinet", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};