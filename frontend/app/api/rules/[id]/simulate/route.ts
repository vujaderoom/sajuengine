import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function POST(request: Request, context: RouteContext) {
  try {
    const { id } = await context.params;
    const body = await request.json().catch(() => null);
    const response = await fetch(
      `${BACKEND_URL}/api/v1/rules/${encodeURIComponent(id)}/simulate`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: body ? JSON.stringify(body) : JSON.stringify({}),
        cache: "no-store",
      },
    );

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        error: "rule_simulation_proxy_failed",
        message: error instanceof Error ? error.message : "unknown error",
        backend_url: BACKEND_URL,
      },
      { status: 502 },
    );
  }
}
