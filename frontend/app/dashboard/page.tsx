"use client";

import { useState } from "react";

type EngineResponse = {
  execution_id: string;
  chart_id: string;
  rule_version: string;
  birth: Record<string, unknown>;
  chart_result: {
    chart: {
      year: string;
      month: string;
      day: string;
      hour: string;
    };
    engine_notes: string[];
  };
  facts: unknown;
  proposals: unknown[];
  counter_rules_applied: unknown[];
  final_result: {
    core_disease: string;
    derived_diseases: string[];
    medicine: string;
    yongshin: string;
    secondary_yongshin: string[];
    depth: number;
    stability_grade: string;
    confidence: number;
  };
  decision_trace: unknown[];
};

export default function DashboardPage() {
  const [name, setName] = useState("sample");
  const [sex, setSex] = useState("male");
  const [birthDatetime, setBirthDatetime] = useState("1991-05-29T16:36:00");
  const [result, setResult] = useState<EngineResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runEngine() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/rule-runner/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          rule_version: "v1.0.0",
          birth: {
            name,
            sex,
            birth_datetime: birthDatetime,
            calendar_type: "solar",
            timezone: "Asia/Seoul",
            location: "Seoul",
          },
        }),
      });

      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }

      setResult(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  const chart = result?.chart_result?.chart;

  return (
    <main>
      <div className="card">
        <h1>Rule Studio Dashboard MVP</h1>
        <p>
          BirthInput → Chart Scaffold → Fact Builder → Rule Runner → Proposal → Counter Rule →
          Finalizer → Decision Trace 흐름 검증 화면입니다.
        </p>
      </div>

      <div className="card">
        <h2>Birth Input</h2>
        <label>
          이름
          <input value={name} onChange={(event) => setName(event.target.value)} />
        </label>
        <label>
          성별
          <select value={sex} onChange={(event) => setSex(event.target.value)}>
            <option value="male">male</option>
            <option value="female">female</option>
            <option value="unknown">unknown</option>
          </select>
        </label>
        <label>
          생년월일시
          <input
            value={birthDatetime}
            onChange={(event) => setBirthDatetime(event.target.value)}
            placeholder="1991-05-29T16:36:00"
          />
        </label>
        <button onClick={runEngine}>{loading ? "실행 중..." : "Rule Runner 실행"}</button>
        {error && <p style={{ color: "#fca5a5" }}>Error: {error}</p>}
      </div>

      {result && chart && (
        <>
          <div className="card">
            <h2>원국 8글자</h2>
            <p>
              <span className="badge">년주: {chart.year}</span>
              <span className="badge">월주: {chart.month}</span>
              <span className="badge">일주: {chart.day}</span>
              <span className="badge">시주: {chart.hour}</span>
            </p>
            <pre>{JSON.stringify(result.chart_result.engine_notes, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Finalizer 결과</h2>
            <p>
              <span className="badge">핵심 병: {result.final_result.core_disease}</span>
            </p>
            <p>
              <span className="badge">약: {result.final_result.medicine}</span>
            </p>
            <p>
              <span className="badge">용신: {result.final_result.yongshin}</span>
            </p>
            <p>Depth: {result.final_result.depth}</p>
            <p>Confidence: {result.final_result.confidence}</p>
          </div>

          <div className="card">
            <h2>Fact JSON</h2>
            <pre>{JSON.stringify(result.facts, null, 2)}</pre>
          </div>
          <div className="card">
            <h2>Proposals</h2>
            <pre>{JSON.stringify(result.proposals, null, 2)}</pre>
          </div>
          <div className="card">
            <h2>Counter Rules</h2>
            <pre>{JSON.stringify(result.counter_rules_applied, null, 2)}</pre>
          </div>
          <div className="card">
            <h2>Decision Trace</h2>
            <pre>{JSON.stringify(result.decision_trace, null, 2)}</pre>
          </div>
        </>
      )}
    </main>
  );
}
