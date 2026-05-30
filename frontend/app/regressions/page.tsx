"use client";

import Link from "next/link";
import { useState } from "react";

type CheckResult = { path: string; expected: unknown; actual: unknown; passed: boolean };
type CaseResult = { id: string; title: string; status: string; path: string; passed: boolean; checks: CheckResult[] };
type RegressionResponse = { total: number; passed: number; failed: number; results: CaseResult[] };

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
      if (!res.ok) throw new Error(json?.message ?? `API error: ${res.status}`);
      setData(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <section className="page-hero">
        <div className="card">
          <h1 className="hero-title">Regression Runner</h1>
          <p className="hero-subtitle">Golden Case 기준으로 원국·Fact·Final Result가 깨졌는지 확인합니다.</p>
          <div className="summary-strip">
            <Link href="/governance">Governance</Link>
            <Link href="/cases">Case Ledger</Link>
            <Link href="/rules">Rule Studio</Link>
          </div>
        </div>
        <div className="card compact">
          <h2>회귀검증</h2>
          <p><span className={`badge ${data?.failed === 0 ? "good" : data ? "bad" : "warn"}`}>{data ? (data.failed === 0 ? "all passed" : "failed") : "not run"}</span></p>
          <button onClick={runRegressions}>{loading ? "실행 중..." : "Regression 실행"}</button>
        </div>
      </section>

      {error && <div className="card"><h2>Error</h2><p style={{ color: "#b91c1c" }}>{error}</p></div>}

      {data && (
        <>
          <section className="grid-3">
            <div className="metric"><div className="metric-label">Total</div><div className="metric-value">{data.total}</div></div>
            <div className="metric"><div className="metric-label">Passed</div><div className="metric-value">{data.passed}</div></div>
            <div className="metric"><div className="metric-label">Failed</div><div className="metric-value">{data.failed}</div></div>
          </section>
          <section className="grid">
            {data.results.map((result) => (
              <article className="card" key={result.id}>
                <p><span className={`badge ${result.passed ? "good" : "bad"}`}>{result.passed ? "PASS" : "FAIL"}</span><span className="badge info">{result.status}</span></p>
                <h2><Link href={`/cases/${encodeURIComponent(result.id)}`}>{result.id}</Link></h2>
                <p className="muted">{result.title}</p>
                <p><span className="badge">checks {result.checks.length}</span><span className="badge">path {result.path}</span></p>
                <details open={!result.passed}>
                  <summary>Checks</summary>
                  <div className="grid">
                    {result.checks.map((check) => (
                      <div className="metric" key={check.path}>
                        <div className="metric-label">{check.path}</div>
                        <p><span className={`badge ${check.passed ? "good" : "bad"}`}>{check.passed ? "PASS" : "FAIL"}</span></p>
                        <details><summary>expected / actual</summary><pre>{JSON.stringify({ expected: check.expected, actual: check.actual }, null, 2)}</pre></details>
                      </div>
                    ))}
                  </div>
                </details>
              </article>
            ))}
          </section>
        </>
      )}
    </main>
  );
}
