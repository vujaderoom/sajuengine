import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
type Context = { params: Promise<{ logicId: string }> };

export async function POST(request: Request, context: Context) {
  const { logicId } = await context.params;
  try {
    const body = await request.json();
    const response = await fetch(`${BACKEND_URL}/api/v1/logic-cards/${encodeURIComponent(logicId)}/toggle`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json({ error: "logic_toggle_proxy_failed", message: error instanceof Error ? error.message : "unknown error", backend_url: BACKEND_URL }, { status: 502 });
  }
}
