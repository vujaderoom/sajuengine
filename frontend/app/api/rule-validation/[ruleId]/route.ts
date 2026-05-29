import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

type RouteContext = {
  params: Promise<{ ruleId: string }>;
};

export async function GET(_request: Request, context: RouteContext) {
  try {
    const { ruleId } = await context.params;
    const response = await fetch(`${BACKEND_URL}/api/v1/rules/${encodeURIComponent(ruleId)}/validate`, {
      method: "GET",
      cache: "no-store",
    });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      { error: "rule_validation_proxy_failed", message: error instanceof Error ? error.message : "unknown error" },
      { status: 502 },
    );
  }
}
