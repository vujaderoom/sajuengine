"use client";

import { useState } from "react";

type LoadedRule = { id: string; title: string; layer: string; target: string; priority: number; enabled: boolean };

type EngineResponse = {
  execution_id: string;
  chart_id: string;
  rule_version: string;
  birth: Record<string, unknown>;
  chart_result: {
    chart: { year: string; month: string; day: string; hour: string };
    ten_gods?: Record<string, string>;
    hidden_stems?: Record<string, string[]>;
    twelve_unseong?: Record<string, string>;
    twelve_shinsal?: Record<string, Record<string, string>>;
    calendar_meta?: Record<string, any>;
    engine_notes: string[];
  };
  facts: Record<string, any>;
  loaded_rules: LoadedRule[];
  proposals: unknown[];
  counter_rules_applied: unknown[];
  final_engine_result?: unknown;
  final_result: { core_disease: string; derived_diseases: string[]; medicine: string; yongshin: string; yongshin_symbols?: string[]; secondary_yongshin: string[]; depth: number; stability_grade: string; confidence: number; confidence_detail?: { level?: string } };
  decision_trace: unknown[];
};

const labels = { year: "년주", month: "월주", day: "일주", hour: "시주" } as const;

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
      const res = await fetch("/api/rule-runner", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rule_version: "v1.0.0", birth: { name, sex, birth_datetime: birthDatetime, calendar_type: "solar", timezone: "Asia/Seoul", location: "Seoul" } }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.message ?? `API error: ${res.status}`);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  const chart = result?.chart_result?.chart;
  const facts = result?.facts;
  const cr = result?.chart_result;

  return (
    <main>
      <section className="page-hero">
        <div className="card">
          <h1 className="hero-title">판단 엔진 대시보드</h1>
          <p className="hero-subtitle">생년월일시를 넣으면 원국, 십성, 지장간, 십이운성, 십이신살, 병·약·용신 판단을 확인합니다.</p>
          <div className="summary-strip"><span className="badge info">Calendar v1</span><span className="badge info">十星</span><span className="badge info">十二運星</span><span className="badge info">十二神殺</span></div>
        </div>
        <div className="card compact"><h2>빠른 실행</h2><p className="muted">기본값은 GC-001 검증 샘플입니다.</p><button onClick={runEngine}>{loading ? "실행 중..." : "Rule Runner 실행"}</button>{error && <p style={{ color: "#b91c1c" }}>Error: {error}</p>}</div>
      </section>

      <section className="card"><h2>Birth Input</h2><div className="grid-3"><label>이름<input value={name} onChange={(event) => setName(event.target.value)} /></label><label>성별<select value={sex} onChange={(event) => setSex(event.target.value)}><option value="male">male</option><option value="female">female</option><option value="unknown">unknown</option></select></label><label>생년월일시<input value={birthDatetime} onChange={(event) => setBirthDatetime(event.target.value)} placeholder="1991-05-29T16:36:00" /></label></div></section>

      {result && chart && cr && (
        <>
          <section className="card">
            <h2>만세력 원국</h2>
            <div className="pillar-row">{(["year", "month", "day", "hour"] as const).map((key) => <div className="pillar" key={key}><small>{labels[key]}</small><strong>{chart[key]}</strong><p className="muted">{cr.ten_gods?.[key] ?? "-"}</p></div>)}</div>
            <p className="summary-strip"><span className="badge info">절입: {String(cr.calendar_meta?.month_boundary_ko ?? cr.calendar_meta?.month_boundary ?? "-")}</span><span className="badge info">월지: {String(cr.calendar_meta?.month_branch ?? "-")}</span><span className="badge info">태양년: {String(cr.calendar_meta?.solar_year_for_pillar ?? "-")}</span></p>
          </section>

          <section className="grid-3"><div className="metric"><div className="metric-label">핵심 병</div><div className="metric-value">{result.final_result.core_disease}</div></div><div className="metric"><div className="metric-label">약</div><div className="metric-value">{result.final_result.medicine}</div></div><div className="metric"><div className="metric-label">용신</div><div className="metric-value">{result.final_result.yongshin}</div></div></section>

          <section className="card">
            <h2>보조 명리표</h2>
            <div className="grid">
              <div className="card compact"><h3>십이운성 / 지장간</h3><div className="grid">{(["year", "month", "day", "hour"] as const).map((key) => <div className="metric" key={key}><div className="metric-label">{labels[key]}</div><p><span className="badge">운성 {cr.twelve_unseong?.[key] ?? "-"}</span></p><p><span className="badge">지장간 {(cr.hidden_stems?.[key] ?? []).join(" · ") || "-"}</span></p></div>)}</div></div>
              <div className="card compact"><h3>십이신살</h3><p className="muted">기본은 년지 기준이며, 일지/월지 기준도 함께 산출합니다.</p>{(["year_base", "day_base", "month_base"] as const).map((base) => <details key={base} open={base === "year_base"}><summary>{base}</summary><p>{(["year", "month", "day", "hour"] as const).map((key) => <span className="badge" key={`${base}-${key}`}>{labels[key]} {cr.twelve_shinsal?.[base]?.[key] ?? "-"}</span>)}</p></details>)}</div>
            </div>
          </section>

          <section className="card"><h2>판단 요약</h2><p><span className="badge good">Depth {result.final_result.depth}</span><span className="badge good">Confidence {result.final_result.confidence}</span><span className="badge info">{result.final_result.confidence_detail?.level ?? "level -"}</span><span className="badge">세부 후보: {result.final_result.yongshin_symbols?.join(", ") || "-"}</span></p><div className="grid"><div className="card compact"><h3>핵심 물상</h3><p>{facts?.water?.image || facts?.moisture_profile?.image || "아직 핵심 물상 설명이 없습니다."}</p></div><div className="card compact"><h3>작동 방식</h3><p><span className="badge">온도: {facts?.temperature_profile?.state ?? "-"}</span><span className="badge">습도: {facts?.moisture_profile?.state ?? "-"}</span><span className="badge">약 작용: {facts?.medicine_need_profile?.primary_action ?? "-"}</span></p></div></div></section>

          <section className="card"><h2>상세 데이터</h2><details><summary>Calendar Result JSON</summary><pre>{JSON.stringify(result.chart_result, null, 2)}</pre></details><details><summary>Structured Profiles</summary><pre>{JSON.stringify({ season_profile: facts?.season_profile, temperature_profile: facts?.temperature_profile, moisture_profile: facts?.moisture_profile, soil_profile: facts?.soil_profile, source_profile: facts?.source_profile, medicine_need_profile: facts?.medicine_need_profile }, null, 2)}</pre></details><details><summary>Formal Final Engine Result</summary><pre>{JSON.stringify(result.final_engine_result, null, 2)}</pre></details><details><summary>Rules / Proposals / Counter Rules</summary><pre>{JSON.stringify({ loaded_rules: result.loaded_rules, proposals: result.proposals, counter_rules: result.counter_rules_applied }, null, 2)}</pre></details><details><summary>Decision Trace</summary><pre>{JSON.stringify(result.decision_trace, null, 2)}</pre></details></section>
        </>
      )}
    </main>
  );
}
