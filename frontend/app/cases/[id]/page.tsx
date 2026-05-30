"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type CaseDetail = {
  id: string;
  title: string;
  status: string;
  version: string;
  path: string;
  birth: Record<string, any>;
  chart: Record<string, any>;
  pillar_text: string;
  expected: Record<string, any>;
  interpretation?: Record<string, any>;
  interpretation_summary: Record<string, any>;
  notes: string[];
  raw_yaml: string;
};

type CaseRunResult = {
  id: string;
  title: string;
  status: string;
  path: string;
  passed: boolean;
  checks: Array<{ path: string; resolved_path: string; expected: unknown; actual: unknown; passed: boolean }>;
  actual_result: any;
};

export default function CaseDetailPage({ params }: { params: { id: string } }) {
  const [item, setItem] = useState<CaseDetail | null>(null);
  const [runResult, setRunResult] = useState<CaseRunResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [runError, setRunError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [runLoading, setRunLoading] = useState(false);

  async function loadCase() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/case-detail/${encodeURIComponent(params.id)}`, { cache: "no-store" });
      const json = await res.json();
      if (!res.ok) throw new Error(json?.detail ?? json?.message ?? `API error: ${res.status}`);
      setItem(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function runCase() {
    setRunLoading(true);
    setRunError(null);
    try {
      const res = await fetch(`/api/case-detail/${encodeURIComponent(params.id)}/run`, { cache: "no-store" });
      const json = await res.json();
      if (!res.ok) throw new Error(json?.detail ?? json?.message ?? `API error: ${res.status}`);
      setRunResult(json);
    } catch (err) {
      setRunError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setRunLoading(false);
    }
  }

  useEffect(() => {
    loadCase();
  }, [params.id]);

  const summary = item?.interpretation_summary ?? {};
  const chart = item?.chart ?? {};
  const interpretation = item?.interpretation ?? {};
  const imageLogic = Array.isArray(interpretation.image_logic) ? interpretation.image_logic : [];
  const linkedRules = Array.isArray(summary.linked_rules) ? summary.linked_rules : [];
  const actualFinal = runResult?.actual_result?.final_result;

  return (
    <main>
      <section className="page-hero">
        <div className="card">
          <h1 className="hero-title">Case Detail</h1>
          <p className="hero-subtitle">저장된 케이스의 원국, 해석 논리, 기대값과 현재 엔진 결과를 비교합니다.</p>
          <div className="summary-strip">
            <Link href="/cases">← Case Ledger</Link>
            <Link href="/regressions">Regression Runner</Link>
          </div>
        </div>
        <div className="card compact">
          <h2>검증</h2>
          <p>
            <span className={`badge ${runResult?.passed ? "good" : runResult ? "bad" : "warn"}`}>case: {runResult ? String(runResult.passed) : "not run"}</span>
            {runResult && <span className="badge info">checks {runResult.checks.length}</span>}
          </p>
          <div className="actions">
            <button className="ghost" onClick={loadCase}>{loading ? "불러오는 중..." : "새로고침"}</button>
            <button onClick={runCase}>{runLoading ? "검증 중..." : "이 케이스 실행"}</button>
          </div>
        </div>
      </section>

      {error && <div className="card"><h2>Error</h2><p style={{ color: "#b91c1c" }}>{error}</p></div>}
      {runError && <div className="card"><h2>Run Error</h2><p style={{ color: "#b91c1c" }}>{runError}</p></div>}

      {item && (
        <>
          <section className="card">
            <p>
              <span className={`badge ${item.status === "approved" ? "good" : "warn"}`}>{item.status}</span>
              <span className="badge info">{item.version}</span>
              <span className="badge">{item.path}</span>
            </p>
            <h2>{item.id}</h2>
            <p className="muted">{item.title}</p>
            <div className="pillar-row">
              <div className="pillar"><small>년</small><strong>{chart.year ?? "-"}</strong></div>
              <div className="pillar"><small>월</small><strong>{chart.month ?? "-"}</strong></div>
              <div className="pillar"><small>일</small><strong>{chart.day ?? "-"}</strong></div>
              <div className="pillar"><small>시</small><strong>{chart.hour ?? "-"}</strong></div>
            </div>
          </section>

          <section className="grid-3">
            <div className="metric"><div className="metric-label">병</div><div className="metric-value">{summary.subtype ?? summary.core_disease ?? "-"}</div></div>
            <div className="metric"><div className="metric-label">약</div><div className="metric-value">{summary.medicine ?? "-"}</div></div>
            <div className="metric"><div className="metric-label">용신</div><div className="metric-value">{summary.yongshin ?? "-"}</div></div>
          </section>

          <section className="grid">
            <div className="card">
              <h2>해석 논리</h2>
              {imageLogic.length ? imageLogic.map((line: string) => <p key={line}><span className="badge info">logic</span> {line}</p>) : <p className="muted">저장된 image_logic가 없습니다.</p>}
              <details>
                <summary>Disease / Medicine / Yongshin Logic</summary>
                <pre>{JSON.stringify(interpretation, null, 2)}</pre>
              </details>
            </div>
            <div className="card">
              <h2>연결 룰</h2>
              {linkedRules.length ? linkedRules.map((rule: string) => <p key={rule}><Link href={`/rules/${encodeURIComponent(rule)}`}>{rule}</Link></p>) : <p className="muted">연결된 룰이 없습니다.</p>}
              <p className="summary-strip">
                {(summary.yongshin_symbols ?? []).map((symbol: string) => <span className="badge" key={symbol}>{symbol}</span>)}
              </p>
            </div>
          </section>

          {runResult && (
            <section className="card">
              <h2>Expected vs Actual</h2>
              {actualFinal && <p><span className="badge">actual 병: {actualFinal.core_disease}</span><span className="badge">actual 약: {actualFinal.medicine}</span><span className="badge">actual 용신: {actualFinal.yongshin}</span></p>}
              <div className="grid">
                {runResult.checks.map((check) => (
                  <div className="metric" key={check.path}>
                    <div className="metric-label">{check.path}</div>
                    <p><span className={`badge ${check.passed ? "good" : "bad"}`}>{check.passed ? "PASS" : "FAIL"}</span></p>
                    <details><summary>expected / actual</summary><pre>{JSON.stringify({ expected: check.expected, actual: check.actual, resolved_path: check.resolved_path }, null, 2)}</pre></details>
                  </div>
                ))}
              </div>
              <details><summary>Actual Result JSON</summary><pre>{JSON.stringify(runResult.actual_result, null, 2)}</pre></details>
            </section>
          )}

          <section className="card">
            <h2>상세 데이터</h2>
            <details><summary>Birth</summary><pre>{JSON.stringify(item.birth, null, 2)}</pre></details>
            <details><summary>Expected</summary><pre>{JSON.stringify(item.expected, null, 2)}</pre></details>
            <details><summary>Notes</summary><pre>{item.notes?.join("\n")}</pre></details>
            <details><summary>Raw YAML</summary><pre>{item.raw_yaml}</pre></details>
          </section>
        </>
      )}
    </main>
  );
}
