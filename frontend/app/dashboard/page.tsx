"use client";

import { useState } from "react";

export default function DashboardPage() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function runEngine() {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/rule-runner/execute", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({rule_version: "v1.0.0"})
      });
      setResult(await res.json());
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <div className="card">
        <h1>Rule Studio Dashboard MVP</h1>
        <p>Rule Runner → Proposal → Counter Rule → Finalizer → Decision Trace 흐름 검증 화면입니다.</p>
        <button onClick={runEngine}>{loading ? "실행 중..." : "Rule Runner 실행"}</button>
      </div>

      {result && (
        <>
          <div className="card">
            <h2>Finalizer 결과</h2>
            <p><span className="badge">핵심 병: {result.final_result.core_disease}</span></p>
            <p><span className="badge">약: {result.final_result.medicine}</span></p>
            <p><span className="badge">용신: {result.final_result.yongshin}</span></p>
            <p>Depth: {result.final_result.depth}</p>
            <p>Confidence: {result.final_result.confidence}</p>
          </div>

          <div className="card"><h2>Fact JSON</h2><pre>{JSON.stringify(result.facts, null, 2)}</pre></div>
          <div className="card"><h2>Proposals</h2><pre>{JSON.stringify(result.proposals, null, 2)}</pre></div>
          <div className="card"><h2>Decision Trace</h2><pre>{JSON.stringify(result.decision_trace, null, 2)}</pre></div>
        </>
      )}
    </main>
  );
}
