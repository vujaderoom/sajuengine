"use client";

import { useEffect, useState } from "react";

type Candidate = {
  id: string;
  title: string;
  status: string;
  enabled: boolean;
  source_case_id: string;
  source_case_title: string;
  source_case_path: string;
  layer: string;
  target: string;
  priority: number;
  propose: { candidate_type?: string; value?: string; symbols?: string[]; action?: string; score_delta?: number; reason?: string };
  expected: Record<string, any>;
};

type CandidateDetail = {
  candidate: Candidate;
  source_case: Record<string, any>;
  raw_candidate_yaml: string;
  normalized_rule_yaml: string;
  validation: { valid: boolean; errors: string[]; warnings: string[] };
};

function badgeClass(value?: string) {
  if (value === "火" || value === "valid" || value === "published") return "good";
  if (value === "水" || value === "invalid") return "bad";
  return "warn";
}

export default function RuleCandidatesPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [detail, setDetail] = useState<CandidateDetail | null>(null);
  const [impact, setImpact] = useState<any>(null);
  const [publishResult, setPublishResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadCandidates() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/rule-candidates", { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.message ?? `API error ${res.status}`);
      setCandidates(data.candidates ?? []);
      if (!selectedId && data.candidates?.[0]?.id) setSelectedId(data.candidates[0].id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function loadDetail(id: string) {
    if (!id) return;
    setLoading(true);
    setError(null);
    setPublishResult(null);
    try {
      const [detailRes, impactRes] = await Promise.all([
        fetch(`/api/rule-candidates/${encodeURIComponent(id)}`, { cache: "no-store" }),
        fetch(`/api/rule-candidates/${encodeURIComponent(id)}/preview-impact`, { cache: "no-store" }),
      ]);
      const detailData = await detailRes.json();
      const impactData = await impactRes.json();
      if (!detailRes.ok) throw new Error(detailData?.message ?? `detail API error ${detailRes.status}`);
      if (!impactRes.ok) throw new Error(impactData?.message ?? `impact API error ${impactRes.status}`);
      setDetail(detailData);
      setImpact(impactData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function publish(enable: boolean) {
    if (!selectedId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/rule-candidates/${encodeURIComponent(selectedId)}/publish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ version: "v1.0.0", enable, overwrite: false, run_regression_after_publish: true }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.message ?? `publish API error ${res.status}`);
      setPublishResult(data);
      await loadCandidates();
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCandidates();
  }, []);

  useEffect(() => {
    if (selectedId) loadDetail(selectedId);
  }, [selectedId]);

  return (
    <main>
      <section className="page-hero">
        <div className="card">
          <h1 className="hero-title">Rule Candidate Review</h1>
          <p className="hero-subtitle">케이스에서 생성된 룰 후보를 검토하고, 영향 미리보기 후 case_derived 룰로 publish합니다.</p>
          <div className="summary-strip"><span className="badge info">I-2</span><span className="badge info">Candidate Review</span><span className="badge warn">기본 publish는 disabled 권장</span></div>
        </div>
        <div className="card compact"><h2>상태</h2><p><span className="badge info">후보 {candidates.length}개</span>{loading && <span className="badge warn">로딩 중</span>}</p>{error && <p style={{ color: "#b91c1c" }}>Error: {error}</p>}<button onClick={loadCandidates}>새로고침</button></div>
      </section>

      <section className="grid" style={{ gridTemplateColumns: "360px 1fr" }}>
        <div className="card">
          <h2>후보 목록</h2>
          {candidates.length === 0 && <p className="muted">아직 rule_candidate가 포함된 케이스가 없습니다. /cases/new에서 케이스를 저장해보세요.</p>}
          <div className="stack">
            {candidates.map((candidate) => (
              <button key={candidate.id} onClick={() => setSelectedId(candidate.id)} style={{ textAlign: "left", background: selectedId === candidate.id ? "#eef2ff" : "white", color: "#111827", boxShadow: "none", border: "1px solid #e5e7eb" }}>
                <strong>{candidate.title}</strong><br />
                <span className="muted">{candidate.id}</span><br />
                <span className={`badge ${badgeClass(candidate.propose?.value)}`}>{candidate.propose?.value ?? "-"}</span>
                <span className="badge info">{candidate.source_case_id}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="card">
          {!detail && <p className="muted">후보를 선택하세요.</p>}
          {detail && (
            <>
              <h2>{detail.candidate.title}</h2>
              <p className="summary-strip">
                <span className="badge info">{detail.candidate.id}</span>
                <span className={`badge ${detail.validation?.valid ? "good" : "bad"}`}>{detail.validation?.valid ? "valid" : "invalid"}</span>
                <span className={`badge ${badgeClass(detail.candidate.propose?.value)}`}>제안 {detail.candidate.propose?.value ?? "-"}</span>
                <span className="badge">점수 {detail.candidate.propose?.score_delta ?? "-"}</span>
              </p>
              <div className="grid">
                <div className="card compact"><h3>원본 케이스</h3><p><strong>{detail.source_case?.title}</strong></p><p className="muted">{detail.source_case?.id}</p><p>{detail.source_case?.interpretation?.image_logic?.slice?.(0, 3)?.join?.(" / ")}</p></div>
                <div className="card compact"><h3>검증</h3><p>{detail.validation?.errors?.map((x, i) => <span className="badge bad" key={`e-${i}`}>{x}</span>)}</p><p>{detail.validation?.warnings?.map((x, i) => <span className="badge warn" key={`w-${i}`}>{x}</span>)}</p></div>
              </div>
              {impact && <div className="card compact"><h3>Impact Preview</h3><p>{impact.impact_notes?.map((x: string, i: number) => <span className="badge info" key={i}>{x}</span>)}</p><pre>{JSON.stringify({ expected: impact.expected, validation: impact.validation }, null, 2)}</pre></div>}
              <div className="summary-strip">
                <button onClick={() => publish(false)}>검토용 Publish disabled</button>
                <button onClick={() => publish(true)}>활성 Publish enabled</button>
              </div>
              {publishResult && <div className="card compact"><h3>Publish Result</h3><p><span className={`badge ${publishResult.published ? "good" : "warn"}`}>{publishResult.published ? "published" : publishResult.reason}</span><span className="badge info">{publishResult.path}</span></p><pre>{JSON.stringify(publishResult.regression_result ?? publishResult.validation, null, 2)}</pre></div>}
              <details><summary>Normalized Rule YAML</summary><pre>{detail.normalized_rule_yaml}</pre></details>
              <details><summary>Raw Candidate YAML</summary><pre>{detail.raw_candidate_yaml}</pre></details>
            </>
          )}
        </div>
      </section>
    </main>
  );
}
