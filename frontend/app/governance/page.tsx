"use client";

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
  release_readiness: {
    ready_to_release?: boolean;
    status?: string;
    blockers?: string[];
    [key: string]: unknown;
  };
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
      if (!res.ok) throw new Error(json?.message ?? `API error: ${res.status}`);
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

  const ready = Boolean(data?.release_readiness?.ready_to_release);

  return (
    <main>
      <section className="page-hero">
        <div className="card">
          <h1 className="hero-title">Rule Governance</h1>
          <p className="hero-subtitle">룰 검증, 케이스 회귀, 릴리즈 가능 상태를 한눈에 확인합니다.</p>
          <div className="summary-strip">
            <span className={`badge ${ready ? "good" : "bad"}`}>release: {ready ? "ready" : "blocked"}</span>
            <span className="badge info">version {data?.rule_version ?? "v1.0.0"}</span>
          </div>
        </div>
        <div className="card compact">
          <h2>상태 새로고침</h2>
          <p className="muted">룰 변경 후 반드시 Governance와 Regression을 확인하세요.</p>
          <button onClick={loadGovernance}>{loading ? "불러오는 중..." : "Governance 새로고침"}</button>
        </div>
      </section>

      {error && (
        <div className="card">
          <h2>Error</h2>
          <p style={{ color: "#b91c1c" }}>{error}</p>
        </div>
      )}

      {data && (
        <>
          <section className="grid-3">
            <div className="metric">
              <div className="metric-label">Rules</div>
              <div className="metric-value">{data.validation_summary.valid}/{data.validation_summary.total}</div>
              <p className="muted">invalid {data.validation_summary.invalid}, warnings {data.validation_summary.warning_rules}</p>
            </div>
            <div className="metric">
              <div className="metric-label">Golden Cases</div>
              <div className="metric-value">{data.regression_summary.passed}/{data.regression_summary.total}</div>
              <p className="muted">failed {data.regression_summary.failed}</p>
            </div>
            <div className="metric">
              <div className="metric-label">Release</div>
              <div className="metric-value">{ready ? "READY" : "BLOCKED"}</div>
              <p className="muted">{data.release_readiness?.blockers?.join(", ") || "no blockers"}</p>
            </div>
          </section>

          <section className="card">
            <h2>Recommendations</h2>
            <div className="workflow">
              {data.recommendations.map((item) => (
                <div className="step" key={item}>{item}</div>
              ))}
            </div>
          </section>

          <section className="card">
            <h2>상세 검사 결과</h2>
            <details open={data.invalid_rules.length > 0}>
              <summary>Invalid Rules ({data.invalid_rules.length})</summary>
              <pre>{JSON.stringify(data.invalid_rules, null, 2)}</pre>
            </details>
            <details>
              <summary>Warning Rules ({data.warning_rules.length})</summary>
              <pre>{JSON.stringify(data.warning_rules, null, 2)}</pre>
            </details>
            <details>
              <summary>Release Readiness JSON</summary>
              <pre>{JSON.stringify(data.release_readiness, null, 2)}</pre>
            </details>
          </section>
        </>
      )}
    </main>
  );
}
