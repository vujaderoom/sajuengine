"use client";

import Link from "next/link";
import { useState } from "react";

type ReportResponse = {
  engine_result: unknown;
  report_payload: {
    chart: Record<string, unknown>;
    disease_profile: Record<string, unknown>;
    medicine_profile: Record<string, unknown>;
    yongshin: Record<string, unknown>;
    confidence: Record<string, unknown>;
    renderer_guardrails: string[];
    decision_trace_id: string;
    rule_version: string;
  };
};

export default function ReportPreviewPage() {
  const [name, setName] = useState("sample");
  const [sex, setSex] = useState("male");
  const [birthDatetime, setBirthDatetime] = useState("1991-05-29T16:36:00");
  const [data, setData] = useState<ReportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function buildReportPayload() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/reports/preview", {
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

  const payload = data?.report_payload;

  return (
    <main>
      <div className="card">
        <h1>Report Payload Preview</h1>
        <p>LLM이 판단하지 않고 렌더링만 하도록 넘길 ENGINE_RESULT_JSON 미리보기입니다.</p>
        <p>
          <Link href="/dashboard">← Dashboard</Link>{" | "}
          <Link href="/cases">Case Ledger</Link>{" | "}
          <Link href="/rules">Rule Studio</Link>
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
        <button onClick={buildReportPayload}>{loading ? "생성 중..." : "Report Payload 생성"}</button>
      </div>

      {error && (
        <div className="card">
          <h2>Error</h2>
          <p style={{ color: "#fca5a5" }}>{error}</p>
        </div>
      )}

      {payload && (
        <>
          <div className="card">
            <h2>Summary</h2>
            <p>
              <span className="badge">년주: {String(payload.chart.year)}</span>
              <span className="badge">월주: {String(payload.chart.month)}</span>
              <span className="badge">일주: {String(payload.chart.day)}</span>
              <span className="badge">시주: {String(payload.chart.hour)}</span>
            </p>
            <p>
              <span className="badge">핵심 병: {String(payload.disease_profile.core_disease)}</span>
              <span className="badge">약: {String(payload.medicine_profile.name)}</span>
              <span className="badge">용신: {String(payload.yongshin.primary)}</span>
              <span className="badge">confidence: {String(payload.confidence.score)}</span>
            </p>
          </div>

          <div className="card">
            <h2>Renderer Guardrails</h2>
            <pre>{payload.renderer_guardrails.join("\n")}</pre>
          </div>

          <div className="card">
            <h2>ENGINE_RESULT_JSON</h2>
            <pre>{JSON.stringify(payload, null, 2)}</pre>
          </div>
        </>
      )}
    </main>
  );
}
