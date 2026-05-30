"use client";

import { useState } from "react";

type ReportResponse = {
  engine_result: unknown;
  report_payload: {
    chart: Record<string, any>;
    disease_profile: Record<string, any>;
    medicine_profile: Record<string, any>;
    yongshin: Record<string, any>;
    confidence: Record<string, any>;
    renderer_guardrails: string[];
    decision_trace_id: string;
    rule_version: string;
  };
};

type RenderResponse = {
  report_payload: unknown;
  rendered: { report_text: string; renderer_input_json: unknown };
  verifier_result: { passed?: boolean; report_status?: string; failed_reasons?: string[]; warnings?: string[] };
};

export default function ReportPreviewPage() {
  const [name, setName] = useState("sample");
  const [sex, setSex] = useState("male");
  const [birthDatetime, setBirthDatetime] = useState("1991-05-29T16:36:00");
  const [data, setData] = useState<ReportResponse | null>(null);
  const [rendered, setRendered] = useState<RenderResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [renderLoading, setRenderLoading] = useState(false);

  const runnerRequest = {
    rule_version: "v1.0.0",
    birth: { name, sex, birth_datetime: birthDatetime, calendar_type: "solar", timezone: "Asia/Seoul", location: "Seoul" },
  };

  async function buildReportPayload() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/reports/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(runnerRequest),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json?.message ?? `API error: ${res.status}`);
      setData(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function renderReport() {
    setRenderLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/llm/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request: runnerRequest, user_question: "" }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json?.message ?? `API error: ${res.status}`);
      setRendered(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setRenderLoading(false);
    }
  }

  const payload = data?.report_payload;
  const verifierPassed = rendered?.verifier_result?.passed;

  return (
    <main>
      <section className="page-hero">
        <div className="card">
          <h1 className="hero-title">Report Preview</h1>
          <p className="hero-subtitle">엔진이 확정한 ENGINE_RESULT_JSON을 리포트 문장으로 렌더링하고, Output Verifier로 검증합니다.</p>
          <div className="summary-strip">
            <span className="badge info">Payload</span>
            <span className="badge info">Renderer</span>
            <span className="badge info">Verifier</span>
          </div>
        </div>
        <div className="card compact">
          <h2>실행</h2>
          <p>
            <span className={`badge ${payload ? "good" : "warn"}`}>payload {payload ? "ready" : "not built"}</span>
            <span className={`badge ${verifierPassed === true ? "good" : verifierPassed === false ? "bad" : "warn"}`}>verifier {rendered ? rendered.verifier_result?.report_status : "not run"}</span>
          </p>
        </div>
      </section>

      <section className="card">
        <h2>Birth Input</h2>
        <div className="grid-3">
          <label>이름<input value={name} onChange={(event) => setName(event.target.value)} /></label>
          <label>성별<select value={sex} onChange={(event) => setSex(event.target.value)}><option value="male">male</option><option value="female">female</option><option value="unknown">unknown</option></select></label>
          <label>생년월일시<input value={birthDatetime} onChange={(event) => setBirthDatetime(event.target.value)} placeholder="1991-05-29T16:36:00" /></label>
        </div>
        <div className="actions"><button onClick={buildReportPayload}>{loading ? "생성 중..." : "Report Payload 생성"}</button><button onClick={renderReport}>{renderLoading ? "렌더링 중..." : "Report Renderer 초안 실행"}</button></div>
      </section>

      {error && <div className="card"><h2>Error</h2><p style={{ color: "#b91c1c" }}>{error}</p></div>}

      {payload && (
        <>
          <section className="card">
            <h2>Payload Summary</h2>
            <div className="pillar-row"><div className="pillar"><small>년</small><strong>{String(payload.chart.year)}</strong></div><div className="pillar"><small>월</small><strong>{String(payload.chart.month)}</strong></div><div className="pillar"><small>일</small><strong>{String(payload.chart.day)}</strong></div><div className="pillar"><small>시</small><strong>{String(payload.chart.hour)}</strong></div></div>
            <div className="grid-3" style={{ marginTop: 14 }}><div className="metric"><div className="metric-label">핵심 병</div><div className="metric-value">{String(payload.disease_profile.core_disease)}</div></div><div className="metric"><div className="metric-label">약</div><div className="metric-value">{String(payload.medicine_profile.name)}</div></div><div className="metric"><div className="metric-label">용신</div><div className="metric-value">{String(payload.yongshin.primary)}</div></div></div>
          </section>
          <section className="card">
            <h2>Renderer Guardrails</h2>
            <div className="workflow">{payload.renderer_guardrails.map((item) => <div className="step" key={item}>{item}</div>)}</div>
          </section>
        </>
      )}

      {rendered && (
        <section className="grid">
          <div className="card">
            <h2>Report Draft</h2>
            <pre>{rendered.rendered.report_text}</pre>
          </div>
          <div className="card">
            <h2>Output Verifier</h2>
            <p><span className={`badge ${verifierPassed ? "good" : "bad"}`}>{rendered.verifier_result?.report_status}</span></p>
            <details open><summary>Verifier Summary</summary><pre>{JSON.stringify(rendered.verifier_result, null, 2)}</pre></details>
          </div>
        </section>
      )}

      {(payload || rendered) && (
        <section className="card">
          <h2>Raw Data</h2>
          {payload && <details><summary>ENGINE_RESULT_JSON</summary><pre>{JSON.stringify(payload, null, 2)}</pre></details>}
          {rendered && <details><summary>Renderer Input JSON</summary><pre>{JSON.stringify(rendered.rendered.renderer_input_json, null, 2)}</pre></details>}
        </section>
      )}
    </main>
  );
}
