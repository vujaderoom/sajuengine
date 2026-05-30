"use client";

import { useState } from "react";

type LoadedRule = { id: string; title: string; layer: string; target: string; priority: number; enabled: boolean };

type ManseryukPillar = {
  key: "hour" | "day" | "month" | "year";
  label: string;
  pillar: string;
  stem: string;
  branch: string;
  stem_ten_god_ko: string;
  branch_ten_god_ko: string;
  hidden_stems: Array<{ stem: string; stem_ko: string; ten_god_ko: string }>;
  twelve_unseong_ko: string;
  pillar_stem_twelve_unseong_ko: string;
  twelve_shinsal_year_base_ko: string;
  xunkong_ko: string[];
  relative_xunkong: { display_ko: string; is_void: boolean; base_label: string; void_branches_ko: string[] };
};

type EngineResponse = {
  execution_id: string;
  chart_id: string;
  rule_version: string;
  birth: Record<string, unknown>;
  chart_result: {
    chart: { year: string; month: string; day: string; hour: string };
    manseryuk_view?: { pillars: ManseryukPillar[] };
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

function charClass(char: string, kind: "stem" | "branch") {
  if (["戊", "己", "辰", "戌", "丑", "未"].includes(char)) return `${kind}-earth`;
  if (["壬", "癸", "子", "亥"].includes(char)) return `${kind}-water`;
  if (["庚", "辛", "申", "酉"].includes(char)) return `${kind}-metal`;
  if (["丙", "丁", "巳", "午"].includes(char)) return `${kind}-fire`;
  if (["甲", "乙", "寅", "卯"].includes(char)) return `${kind}-wood`;
  return "";
}

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

  const facts = result?.facts;
  const cr = result?.chart_result;
  const board = cr?.manseryuk_view?.pillars ?? [];

  return (
    <main>
      <section className="page-hero">
        <div className="card">
          <h1 className="hero-title">만세력 보드</h1>
          <p className="hero-subtitle">시주·일주·월주·년주를 만세력 앱처럼 한 화면에 정렬합니다. 공망은 요청 기준에 따라 일주는 년공망, 나머지는 일공망 여부를 표시합니다.</p>
          <div className="summary-strip"><span className="badge info">Calendar v1.3</span><span className="badge info">오행 색상 보정</span><span className="badge info">금=흰색</span><span className="badge info">목=초록</span></div>
        </div>
        <div className="card compact"><h2>빠른 실행</h2><p className="muted">기본값은 GC-001 검증 샘플입니다.</p><button onClick={runEngine}>{loading ? "실행 중..." : "Rule Runner 실행"}</button>{error && <p style={{ color: "#b91c1c" }}>Error: {error}</p>}</div>
      </section>

      <section className="card"><h2>Birth Input</h2><div className="grid-3"><label>이름<input value={name} onChange={(event) => setName(event.target.value)} /></label><label>성별<select value={sex} onChange={(event) => setSex(event.target.value)}><option value="male">male</option><option value="female">female</option><option value="unknown">unknown</option></select></label><label>생년월일시<input value={birthDatetime} onChange={(event) => setBirthDatetime(event.target.value)} placeholder="1991-05-29T16:36:00" /></label></div></section>

      {result && cr && (
        <>
          <section className="card">
            <h2>만세력 원판</h2>
            <p className="summary-strip"><span className="badge info">절입: {String(cr.calendar_meta?.month_boundary_ko ?? cr.calendar_meta?.month_boundary ?? "-")}</span><span className="badge info">월지: {String(cr.calendar_meta?.month_branch ?? "-")}</span><span className="badge info">태양년: {String(cr.calendar_meta?.solar_year_for_pillar ?? "-")}</span><span className="badge warn">절기모드: {String(cr.calendar_meta?.solar_term_mode ?? "-")}</span></p>
            <div className="manseryuk-board">
              <div className="manseryuk-grid">
                {board.map((p) => <div className="m-cell m-header" key={`h-${p.key}`}>{p.label}</div>)}
                {board.map((p) => <div className="m-cell m-subheader" key={`tg-${p.key}`}>{p.stem_ten_god_ko}</div>)}
                {board.map((p) => <div className="m-cell m-stem-branch" key={`stem-${p.key}`}><div className="m-ten-god">{p.stem_ten_god_ko}</div><div className={`m-big-char ${p.key === "day" ? "stem-day" : ""} ${charClass(p.stem, "stem")}`}>{p.stem}</div></div>)}
                {board.map((p) => <div className="m-cell m-stem-branch" key={`branch-${p.key}`}><div className="m-ten-god">{p.branch_ten_god_ko}</div><div className={`m-big-char ${charClass(p.branch, "branch")}`}>{p.branch}</div></div>)}
                {board.map((p) => <div className="m-cell m-hidden" key={`hs-${p.key}`}>{p.hidden_stems.map((h) => `${h.stem}${h.ten_god_ko}`).join("\n")}</div>)}
                {board.map((p) => <div className="m-cell m-small" key={`un-day-${p.key}`}>{p.twelve_unseong_ko}</div>)}
                {board.map((p) => <div className="m-cell m-small" key={`un-pillar-${p.key}`}>{p.pillar_stem_twelve_unseong_ko}</div>)}
                {board.map((p) => <div className="m-cell m-small" key={`xk-${p.key}`}><span className={`badge ${p.relative_xunkong?.is_void ? "bad" : "info"}`}>{p.relative_xunkong?.display_ko ?? "-"}</span><br /><span className="muted">{p.relative_xunkong?.base_label ?? ""} {p.relative_xunkong?.void_branches_ko?.join("·") ?? ""}</span></div>)}
                {board.map((p) => <div className="m-cell m-yellow m-small" key={`ss-${p.key}`}>{p.twelve_shinsal_year_base_ko}</div>)}
              </div>
            </div>
          </section>

          <section className="grid-3"><div className="metric"><div className="metric-label">핵심 병</div><div className="metric-value">{result.final_result.core_disease}</div></div><div className="metric"><div className="metric-label">약</div><div className="metric-value">{result.final_result.medicine}</div></div><div className="metric"><div className="metric-label">용신</div><div className="metric-value">{result.final_result.yongshin}</div></div></section>

          <section className="card"><h2>판단 요약</h2><p><span className="badge good">Depth {result.final_result.depth}</span><span className="badge good">Confidence {result.final_result.confidence}</span><span className="badge info">{result.final_result.confidence_detail?.level ?? "level -"}</span><span className="badge">세부 후보: {result.final_result.yongshin_symbols?.join(", ") || "-"}</span></p><div className="grid"><div className="card compact"><h3>핵심 물상</h3><p>{facts?.water?.image || facts?.moisture_profile?.image || "아직 핵심 물상 설명이 없습니다."}</p></div><div className="card compact"><h3>작동 방식</h3><p><span className="badge">온도: {facts?.temperature_profile?.state ?? "-"}</span><span className="badge">습도: {facts?.moisture_profile?.state ?? "-"}</span><span className="badge">약 작용: {facts?.medicine_need_profile?.primary_action ?? "-"}</span></p></div></div></section>

          <section className="card"><h2>상세 데이터</h2><details><summary>Manseryuk View JSON</summary><pre>{JSON.stringify(cr.manseryuk_view, null, 2)}</pre></details><details><summary>Calendar Result JSON</summary><pre>{JSON.stringify(result.chart_result, null, 2)}</pre></details><details><summary>Structured Profiles</summary><pre>{JSON.stringify({ season_profile: facts?.season_profile, temperature_profile: facts?.temperature_profile, moisture_profile: facts?.moisture_profile, soil_profile: facts?.soil_profile, source_profile: facts?.source_profile, medicine_need_profile: facts?.medicine_need_profile }, null, 2)}</pre></details><details><summary>Formal Final Engine Result</summary><pre>{JSON.stringify(result.final_engine_result, null, 2)}</pre></details><details><summary>Rules / Proposals / Counter Rules</summary><pre>{JSON.stringify({ loaded_rules: result.loaded_rules, proposals: result.proposals, counter_rules: result.counter_rules_applied }, null, 2)}</pre></details><details><summary>Decision Trace</summary><pre>{JSON.stringify(result.decision_trace, null, 2)}</pre></details></section>
        </>
      )}
    </main>
  );
}
