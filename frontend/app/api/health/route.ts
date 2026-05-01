/**
 * GET /api/health
 *
 * Proxies to the backend's health endpoint. Used by Docker healthchecks and
 * the header status pill in the chat UI.
 */

import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function GET() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/health`, {
      signal: AbortSignal.timeout(5_000),
      cache: "no-store",
    });
    const json = await res.json().catch(() => ({ status: "unknown" }));
    return NextResponse.json(json, { status: res.status });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json(
      { status: "unreachable", error: message },
      { status: 503 },
    );
  }
}
