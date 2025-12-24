import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(req: NextRequest) {
  const url = req.nextUrl.clone();
  const path = url.pathname;


  const publicPaths = ["/", "/role", "/login"];
  if (publicPaths.includes(path)) return NextResponse.next();
  return NextResponse.next();
}
