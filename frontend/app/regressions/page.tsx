"use client";

import Link from "next/link";
import { useState } from "react";

type CheckResult = {
  path: string;
  expected: unknown;
  actual: unknown;
  passed: boolean;
};

type CaseResult = {
  id: string;
  title: string;
  status: string;
  path: string;
  passed: boolean;
  checks: CheckResult[];
};

type RegressionResponse = {
  total: number;
  passed: number;
  failed: number;
  results: CaseResult[];
};

export default function RegressionsPage() {
  const [data, setData] = useState<RegressionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function runRegressions() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/regressions/run", { cache: "no-store" });
      const json = await res.json();
      if (!res.ok) {
        throw new Error(json?.message ?? `API error: ${res.status}`);
      }
      setData(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <div className="card">
        <h1>Regression Runner</h1>
        <p>Golden Case 기준으로 원국·Fact·Final Result가 깨졌는지 확인합니다.</p>
        <p>
          <Link href="/dashboard">← Dashboard</Link>{" | "}
          <Link href="/rules">Rule Studio</Link>
        </p>
        <button onClick={runRegressions}>{loading ? "실행 중..." : "Regression 실행"}</button>
      </div>

      {error && (
        <div className="card">
          <h2>Error</h2>
          <p style={{ color: "#fca5a5" }}>{error}</p>
        </div>
      )}

      {data && (
        <>
          <div className="card">
            <h2>Summary</h2>
            <p>
              <span className="badge">total: {data.total}</span>
              <span className="badge">passed: {data.passed}</span>
              <span className="badge">failed: {data.failed}</span>
            </p>
          </div>

          {data.results.map((result) => (
            <div className="card" key={result.id}>
              <h2>{result.id}</h2>
              <p>{result.title}</p>
              <p>
                <span className="badge">status: {result.status}</span>
                <span className="badge">passed: {String(result.passed)}</span>
              </p>
              <pre>{result.path}</pre>

              <h3>Checks</h3>
              {result.checks.map((check) => (
                <div className="card" key={check.path}>
                  <p>
                    <strong>{check.path}</strong>
                  </p>
                  <p>
                    <span className="badge">passed: {String(check.passed)}</span>
                  </p>
                  <pre>{JSON.stringify({ expected: check.expected, actual: check.actual }, null, 2)}</pre>
                </div>
              ))}
            </div>
          ))}
        </>
      )}
    </main>
  );
}
