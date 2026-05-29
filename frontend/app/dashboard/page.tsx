"use client";

import Link from "next/link";
import { useState } from "react";

type LoadedRule = {
  id: string;
  title: string;
  layer: string;
  target: string;
  priority: number;
  enabled: boolean;
};

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
  facts: Record<string, unknown>;
  loaded_rules: LoadedRule[];
  proposals: unknown[];
  counter_rules_applied: unknown[];
  final_engine_result?: unknown;
  final_result: {
    core_disease: string;
    derived_diseases: string[];
    medicine: string;
    yongshin: string;
    yongshin_symbols?: string[];
    secondary_yongshin: string[];
    depth: number;
    stability_grade: string;
    confidence: number;
    confidence_detail?: { level?: string };
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
  const [lastApiUrl, setLastApiUrl] = useState<string | null>(null);

  async function runEngine() {
    setLoading(true);
    setError(null);
    try {
      const apiUrl = "/api/rule-runner";
      setLastApiUrl(apiUrl);

      const res = await fetch(apiUrl, {
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

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data?.message ?? `API error: ${res.status}`);
      }

      setResult(data);
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
          BirthInput → Calendar Engine → Fact Builder v2 → YAML Rule DSL → Formal Finalizer →
          ReportPayload 흐름 검증 화면입니다.
        </p>
        <p>
          <Link href="/cases">Case Ledger 열기 →</Link>{" | "}
          <Link href="/rules">Rule Studio 열기 →</Link>{" | "}
          <Link href="/regressions">Regression Runner 열기 →</Link>{" | "}
          <Link href="/reports/preview">Report Payload Preview 열기 →</Link>
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
        {lastApiUrl && <p style={{ color: "#94a3b8" }}>API: {lastApiUrl}</p>}
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
              <span className="badge">약: {result.final_result.medicine}</span>
              <span className="badge">용신: {result.final_result.yongshin}</span>
            </p>
            {result.final_result.yongshin_symbols?.length ? (
              <p>
                <span className="badge">세부 후보: {result.final_result.yongshin_symbols.join(", ")}</span>
              </p>
            ) : null}
            <p>
              <span className="badge">Depth: {result.final_result.depth}</span>
              <span className="badge">Confidence: {result.final_result.confidence}</span>
              <span className="badge">Level: {result.final_result.confidence_detail?.level ?? "-"}</span>
            </p>
          </div>

          <div className="card">
            <h2>Structured Profiles</h2>
            <pre>
              {JSON.stringify(
                {
                  season_profile: result.facts.season_profile,
                  temperature_profile: result.facts.temperature_profile,
                  moisture_profile: result.facts.moisture_profile,
                  soil_profile: result.facts.soil_profile,
                  source_profile: result.facts.source_profile,
                  medicine_need_profile: result.facts.medicine_need_profile,
                },
                null,
                2,
              )}
            </pre>
          </div>

          <div className="card">
            <h2>Formal Final Engine Result</h2>
            <pre>{JSON.stringify(result.final_engine_result, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Loaded YAML Rules</h2>
            <pre>{JSON.stringify(result.loaded_rules, null, 2)}</pre>
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
