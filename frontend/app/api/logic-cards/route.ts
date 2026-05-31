import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const includeDisabled = searchParams.get("include_disabled") ?? "true";
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/logic-cards?include_disabled=${includeDisabled}`, { cache: "no-store" });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json({ error: "logic_cards_proxy_failed", message: error instanceof Error ? error.message : "unknown error", backend_url: BACKEND_URL }, { status: 502 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const response = await fetch(`${BACKEND_URL}/api/v1/logic-cards`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json({ error: "logic_card_create_proxy_failed", message: error instanceof Error ? error.message : "unknown error", backend_url: BACKEND_URL }, { status: 502 });
  }
}
