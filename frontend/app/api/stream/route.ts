/**
 * POST /api/stream
 *
 * Streaming chat proxy. Forwards to the FastAPI backend's streaming RAG
 * endpoint (/api/v1/stream) and pipes the SSE/JSONL response back to the
 * browser unchanged. The frontend consumes this as a `ReadableStream`.
 */

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(req: Request) {
  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return new Response("Invalid JSON body", { status: 400 });
  }

  const upstream = `${BACKEND_URL}/api/v1/stream`;
  const res = await fetch(upstream, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    // Stream for up to 2 minutes before aborting.
    signal: AbortSignal.timeout(120_000),
  });

  if (!res.ok || !res.body) {
    const text = await res.text().catch(() => "");
    return new Response(
      JSON.stringify({
        error: `Backend responded with ${res.status}`,
        detail: text.slice(0, 1000),
      }),
      {
        status: res.status || 502,
        headers: { "Content-Type": "application/json" },
      },
    );
  }

  return new Response(res.body, {
    status: 200,
    headers: {
      "Content-Type":
        res.headers.get("Content-Type") ?? "application/x-ndjson; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      "X-Accel-Buffering": "no",
    },
  });
}
