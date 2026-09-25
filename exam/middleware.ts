import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// ⚠️ Shu nomni login handler'ingiz ishlatayotgan nom bilan moslang!
// Variantlar: "maestro_session", "exam_token", "access_token"
const SESSION_COOKIE = "maestro_session";

// Faqat EXACT match — prefix matching emas
const PUBLIC_PATHS = new Set([
  "/",
  "/login",
  "/register",
  "/api",              // agar Next.js API routes bo'lsa
]);

// Public bo'lishi kerak bo'lgan prefix'lar
const PUBLIC_PREFIXES = [
  "/_next",
  "/favicon",
  "/assets",
  "/images",
];

function isPublicPath(pathname: string): boolean {
  if (PUBLIC_PATHS.has(pathname)) return true;
  return PUBLIC_PREFIXES.some((prefix) => pathname.startsWith(prefix));
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 1. Static fayllarni darhol o'tkazib yuborish
  if (pathname.includes(".") || pathname.startsWith("/_next")) {
    return NextResponse.next();
  }

  const session = request.cookies.get(SESSION_COOKIE);
  const publicPath = isPublicPath(pathname);

  // 2. Session bor + public sahifada → cabinet'ga
  if (session?.value && publicPath && pathname !== "/cabinet") {
    return NextResponse.redirect(new URL("/cabinet", request.url));
  }

  // 3. Session yo'q + protected sahifada → login'ga
  if (!session?.value && !publicPath) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico
     * - public folder files (.*\..*)
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)",
  ],
};