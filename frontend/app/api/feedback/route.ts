/**
 * POST /api/feedback
 *
 * Proxies a thumbs-up/down to the Langfuse-backed feedback endpoint.
 */

import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(req: Request) {
  let body: { trace_id?: string; score?: number; comment?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  if (!body.trace_id || typeof body.score !== "number") {
    return NextResponse.json(
      { error: "`trace_id` and numeric `score` are required" },
      { status: 400 },
    );
  }

  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(15_000),
    });
    const json = await res.json().catch(() => ({}));
    return NextResponse.json(json, { status: res.status });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json(
      { error: "Backend unreachable", detail: message },
      { status: 502 },
    );
  }
}
