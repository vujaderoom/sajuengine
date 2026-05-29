import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/cases`, {
      method: "GET",
      cache: "no-store",
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        error: "cases_proxy_failed",
        message: error instanceof Error ? error.message : "unknown error",
        backend_url: BACKEND_URL,
      },
      { status: 502 },
    );
  }
}
