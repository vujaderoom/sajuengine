"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type GovernanceResponse = {
  rule_version: string;
  validation_summary: {
    total: number;
    valid: number;
    invalid: number;
    warning_rules: number;
  };
  regression_summary: {
    total: number;
    passed: number;
    failed: number;
  };
  release_readiness: unknown;
  invalid_rules: unknown[];
  warning_rules: unknown[];
  recommendations: string[];
};

export default function GovernancePage() {
  const [data, setData] = useState<GovernanceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadGovernance() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/governance", { cache: "no-store" });
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

  useEffect(() => {
    loadGovernance();
  }, []);

  return (
    <main>
      <div className="card">
        <h1>Rule Governance Dashboard</h1>
        <p>룰 검증, 회귀 테스트, 릴리즈 가능 상태를 한 번에 확인합니다.</p>
        <p>
          <Link href="/dashboard">← Dashboard</Link>{" | "}
          <Link href="/rules">Rule Studio</Link>{" | "}
          <Link href="/regressions">Regression Runner</Link>{" | "}
          <Link href="/cases">Case Ledger</Link>
        </p>
        <button onClick={loadGovernance}>{loading ? "불러오는 중..." : "Governance 새로고침"}</button>
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
              <span className="badge">rule version: {data.rule_version}</span>
              <span className="badge">rules: {data.validation_summary.total}</span>
              <span className="badge">valid: {data.validation_summary.valid}</span>
              <span className="badge">invalid: {data.validation_summary.invalid}</span>
              <span className="badge">warning rules: {data.validation_summary.warning_rules}</span>
            </p>
            <p>
              <span className="badge">cases: {data.regression_summary.total}</span>
              <span className="badge">passed: {data.regression_summary.passed}</span>
              <span className="badge">failed: {data.regression_summary.failed}</span>
            </p>
          </div>

          <div className="card">
            <h2>Release Readiness</h2>
            <pre>{JSON.stringify(data.release_readiness, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Invalid Rules</h2>
            <pre>{JSON.stringify(data.invalid_rules, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Warning Rules</h2>
            <pre>{JSON.stringify(data.warning_rules, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Recommendations</h2>
            <pre>{data.recommendations.join("\n")}</pre>
          </div>
        </>
      )}
    </main>
  );
}
