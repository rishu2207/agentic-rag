/**
 * POST /api/chat
 *
 * Proxies a chat request to the FastAPI backend's agentic RAG endpoint.
 *
 * Body: { query: string; top_k?: number; use_hybrid?: boolean; model?: string; categories?: string[] }
 * Returns: AgenticAskResponse JSON from the backend.
 *
 * This is a server-only route handler, so the internal BACKEND_URL never
 * leaves the container network.
 */

import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

type ChatRequest = {
  query: string;
  top_k?: number;
  use_hybrid?: boolean;
  model?: string;
  categories?: string[] | null;
};

export async function POST(req: Request) {
  let body: ChatRequest;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  if (!body?.query || typeof body.query !== "string") {
    return NextResponse.json(
      { error: "`query` is required and must be a string" },
      { status: 400 },
    );
  }

  const upstream = `${BACKEND_URL}/api/v1/ask-agentic`;

  try {
    const res = await fetch(upstream, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: body.query,
        top_k: body.top_k ?? 5,
        use_hybrid: body.use_hybrid ?? true,
        model: body.model,
        categories: body.categories ?? null,
      }),
      // Agentic RAG can take 30+ seconds when using local Ollama.
      // Keep the timeout generous but explicit.
      signal: AbortSignal.timeout(120_000),
    });

    const text = await res.text();
    if (!res.ok) {
      return NextResponse.json(
        {
          error: `Backend responded with ${res.status}`,
          detail: text.slice(0, 1000),
        },
        { status: res.status },
      );
    }

    try {
      return NextResponse.json(JSON.parse(text));
    } catch {
      return NextResponse.json(
        { error: "Backend returned invalid JSON", detail: text.slice(0, 500) },
        { status: 502 },
      );
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json(
      {
        error: "Could not reach the backend",
        detail: message,
        upstream,
      },
      { status: 502 },
    );
  }
}
