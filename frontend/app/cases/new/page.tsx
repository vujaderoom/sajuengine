"use client";

import Link from "next/link";
import { useState } from "react";

type PreviewResponse = {
  case_id: string;
  chart_result: unknown;
  engine_result: any;
  linked_rules: string[];
  rule_improvement_candidates: unknown[];
  case_yaml: unknown;
  raw_yaml: string;
  save_instruction: string;
};

type StructureResponse = {
  structured_authoring: Record<string, unknown>;
  confidence: string;
  extraction_notes: string[];
  preview: PreviewResponse;
};

type SaveResponse = {
  saved: boolean;
  reason?: string;
  path?: string;
  case_id?: string;
  single_case_result?: any;
  regression_result?: any;
  preview?: PreviewResponse;
};

const steps = ["기본정보", "물상입력", "구조검토", "저장검증"];

export default function NewCasePage() {
  const [activeStep, setActiveStep] = useState(0);
  const [caseId, setCaseId] = useState("GC-DRAFT-001");
  const [title, setTitle] = useState("새 해석 케이스 초안");
  const [name, setName] = useState("draft");
  const [sex, setSex] = useState("unknown");
  const [birthDatetime, setBirthDatetime] = useState("1991-05-29T16:36:00");
  const [naturalLogicText, setNaturalLogicText] = useState(
    "己土는 巳月에 태어났고 癸水·壬申·亥水가 있어 따뜻한 비가 논을 잠기게 한다. 문제는 한랭이 아니라 수습 과다·침수형이다. 火로 말림·건조·증발해야 하므로 용신은 巳火, 午火, 丙火, 丁火로 본다. 庚金은 주용신이 아니라 조건부 보조 후보로 본다.",
  );
  const [imageLogicText, setImageLogicText] = useState(
    "己土는 논밭·습토의 물상으로 본다.\n巳月이라 계절 자체가 춥지는 않다.\n癸水·壬水·亥水·申金 수원이 이어진다.",
  );
  const [diseaseCore, setDiseaseCore] = useState("기후형 병");
  const [diseaseSubtype, setDiseaseSubtype] = useState("수습 과다·침수형");
  const [diseaseReason, setDiseaseReason] = useState("巳月 己土에 수원이 이어져 습이 과해진다.");
  const [medicineType, setMedicineType] = useState("기후 복원형");
  const [medicineAction, setMedicineAction] = useState("말림·건조·증발");
  const [medicineReason, setMedicineReason] = useState("火는 온도 회복이 아니라 물을 말리고 증발시키는 작용이다.");
  const [yongshinPrimary, setYongshinPrimary] = useState("火");
  const [yongshinSymbolsText, setYongshinSymbolsText] = useState("巳火, 午火, 丙火, 丁火");
  const [notesText, setNotesText] = useState("해석자 검토 필요");
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [structured, setStructured] = useState<StructureResponse | null>(null);
  const [saveResult, setSaveResult] = useState<SaveResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [structuring, setStructuring] = useState(false);
  const [saving, setSaving] = useState(false);

  const authoringPayload = {
    case_id: caseId,
    title,
    status: "draft",
    version: "1.0.0",
    birth: { name, sex, birth_datetime: birthDatetime, calendar_type: "solar", timezone: "Asia/Seoul", location: "Seoul" },
    image_logic_text: imageLogicText,
    disease_core: diseaseCore,
    disease_subtype: diseaseSubtype,
    disease_reason: diseaseReason,
    medicine_type: medicineType,
    medicine_action: medicineAction,
    medicine_reason: medicineReason,
    yongshin_primary: yongshinPrimary,
    yongshin_symbols: yongshinSymbolsText.split(",").map((item) => item.trim()).filter(Boolean),
    excluded_candidates: [],
    notes: notesText.split("\n").map((item) => item.trim()).filter(Boolean),
  };

  function applyStructuredAuthoring(payload: Record<string, unknown>) {
    setImageLogicText(String(payload.image_logic_text ?? imageLogicText));
    setDiseaseCore(String(payload.disease_core ?? diseaseCore));
    setDiseaseSubtype(String(payload.disease_subtype ?? diseaseSubtype));
    setDiseaseReason(String(payload.disease_reason ?? diseaseReason));
    setMedicineType(String(payload.medicine_type ?? medicineType));
    setMedicineAction(String(payload.medicine_action ?? medicineAction));
    setMedicineReason(String(payload.medicine_reason ?? medicineReason));
    setYongshinPrimary(String(payload.yongshin_primary ?? yongshinPrimary));
    setYongshinSymbolsText(Array.isArray(payload.yongshin_symbols) ? payload.yongshin_symbols.join(", ") : yongshinSymbolsText);
    setNotesText(Array.isArray(payload.notes) ? payload.notes.join("\n") : notesText);
  }

  async function structureNaturalLogic() {
    setStructuring(true);
    setError(null);
    setSaveResult(null);
    try {
      const res = await fetch("/api/cases/authoring/structure-natural-logic", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ case_id: caseId, title, birth: authoringPayload.birth, natural_logic_text: naturalLogicText }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json?.message ?? `API error: ${res.status}`);
      setStructured(json);
      setPreview(json.preview);
      applyStructuredAuthoring(json.structured_authoring);
      setActiveStep(2);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setStructuring(false);
    }
  }

  async function generatePreview() {
    setLoading(true);
    setError(null);
    setSaveResult(null);
    try {
      const res = await fetch("/api/cases/authoring/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(authoringPayload),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json?.message ?? `API error: ${res.status}`);
      setPreview(json);
      setActiveStep(3);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function saveCase() {
    setSaving(true);
    setError(null);
    try {
      const res = await fetch("/api/cases/authoring/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ authoring: authoringPayload, overwrite: false, run_regression_after_save: true }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json?.message ?? `API error: ${res.status}`);
      setSaveResult(json);
      if (json.preview) setPreview(json.preview);
      setActiveStep(3);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setSaving(false);
    }
  }

  const chart = preview?.chart_result && typeof preview.chart_result === "object" ? (preview.chart_result as any).chart : null;
  const finalResult = preview?.engine_result?.final_result;
  const singlePassed = saveResult?.single_case_result?.passed;
  const regressionFailed = saveResult?.regression_result?.failed;

  return (
    <main>
      <section className="page-hero">
        <div className="card">
          <h1 className="hero-title">New Case Authoring</h1>
          <p className="hero-subtitle">자연어 물상 설명을 구조화하고, Case YAML로 저장한 뒤 회귀검증까지 이어갑니다.</p>
        </div>
        <div className="card compact">
          <h2>진행 상태</h2>
          <p>
            <span className={`badge ${structured ? "good" : "warn"}`}>구조화 {structured ? "완료" : "대기"}</span>
            <span className={`badge ${preview ? "good" : "warn"}`}>Preview {preview ? "완료" : "대기"}</span>
            <span className={`badge ${saveResult?.saved ? "good" : saveResult ? "bad" : "warn"}`}>저장 {saveResult?.saved ? "완료" : "대기"}</span>
          </p>
        </div>
      </section>

      <section className="card">
        <h2>작업 순서</h2>
        <div className="workflow">
          {steps.map((step, index) => (
            <button key={step} className={activeStep === index ? "" : "ghost"} onClick={() => setActiveStep(index)}>
              {step}
            </button>
          ))}
        </div>
      </section>

      {error && <div className="card"><h2>Error</h2><p style={{ color: "#b91c1c" }}>{error}</p></div>}

      {activeStep === 0 && (
        <section className="card">
          <h2>1. 기본 정보</h2>
          <div className="grid">
            <label>Case ID<input value={caseId} onChange={(event) => setCaseId(event.target.value)} /></label>
            <label>Title<input value={title} onChange={(event) => setTitle(event.target.value)} /></label>
            <label>이름<input value={name} onChange={(event) => setName(event.target.value)} /></label>
            <label>성별<select value={sex} onChange={(event) => setSex(event.target.value)}><option value="male">male</option><option value="female">female</option><option value="unknown">unknown</option></select></label>
            <label>생년월일시<input value={birthDatetime} onChange={(event) => setBirthDatetime(event.target.value)} /></label>
          </div>
          <div className="actions"><button onClick={() => setActiveStep(1)}>다음: 물상 입력</button></div>
        </section>
      )}

      {activeStep === 1 && (
        <section className="card">
          <h2>2. 자연어 물상 입력</h2>
          <p className="muted">네가 보는 논리 그대로 길게 입력해도 됩니다. 지금은 규칙 기반 구조화 scaffold입니다.</p>
          <label>Natural Logic Text<textarea value={naturalLogicText} onChange={(event) => setNaturalLogicText(event.target.value)} rows={10} /></label>
          <div className="actions">
            <button className="ghost" onClick={() => setActiveStep(0)}>이전</button>
            <button onClick={structureNaturalLogic}>{structuring ? "구조화 중..." : "물상 논리 자동 구조화"}</button>
          </div>
        </section>
      )}

      {activeStep === 2 && (
        <section className="card">
          <h2>3. 구조화 결과 검토</h2>
          {structured && <p>{structured.extraction_notes.map((note) => <span className="badge info" key={note}>{note}</span>)}</p>}
          <div className="grid">
            <label>Image Logic<textarea value={imageLogicText} onChange={(event) => setImageLogicText(event.target.value)} rows={8} /></label>
            <div>
              <label>Disease Core<input value={diseaseCore} onChange={(event) => setDiseaseCore(event.target.value)} /></label>
              <label>Disease Subtype<input value={diseaseSubtype} onChange={(event) => setDiseaseSubtype(event.target.value)} /></label>
              <label>Medicine Type<input value={medicineType} onChange={(event) => setMedicineType(event.target.value)} /></label>
              <label>Medicine Action<input value={medicineAction} onChange={(event) => setMedicineAction(event.target.value)} /></label>
              <label>Yongshin Primary<input value={yongshinPrimary} onChange={(event) => setYongshinPrimary(event.target.value)} /></label>
              <label>Yongshin Symbols<input value={yongshinSymbolsText} onChange={(event) => setYongshinSymbolsText(event.target.value)} /></label>
            </div>
          </div>
          <details><summary>Reason / Notes 편집</summary>
            <label>Disease Reason<textarea value={diseaseReason} onChange={(event) => setDiseaseReason(event.target.value)} rows={3} /></label>
            <label>Medicine Reason<textarea value={medicineReason} onChange={(event) => setMedicineReason(event.target.value)} rows={3} /></label>
            <label>Notes<textarea value={notesText} onChange={(event) => setNotesText(event.target.value)} rows={4} /></label>
          </details>
          <div className="actions">
            <button className="ghost" onClick={() => setActiveStep(1)}>이전</button>
            <button onClick={generatePreview}>{loading ? "생성 중..." : "Case YAML Preview 생성"}</button>
          </div>
        </section>
      )}

      {activeStep === 3 && (
        <section className="card">
          <h2>4. 저장 / 회귀검증</h2>
          {preview ? (
            <>
              <div className="grid-3">
                <div className="metric"><div className="metric-label">Case</div><div className="metric-value">{preview.case_id}</div></div>
                <div className="metric"><div className="metric-label">Linked Rules</div><div className="metric-value">{preview.linked_rules.length}</div></div>
                <div className="metric"><div className="metric-label">Rule Gaps</div><div className="metric-value">{preview.rule_improvement_candidates.length}</div></div>
              </div>
              {chart && <div className="card compact"><h3>계산 원국</h3><div className="pillar-row"><div className="pillar"><small>년</small><strong>{chart.year}</strong></div><div className="pillar"><small>월</small><strong>{chart.month}</strong></div><div className="pillar"><small>일</small><strong>{chart.day}</strong></div><div className="pillar"><small>시</small><strong>{chart.hour}</strong></div></div></div>}
              {finalResult && <div className="card compact"><h3>현재 엔진 판단</h3><p><span className="badge">병: {finalResult.core_disease}</span><span className="badge">약: {finalResult.medicine}</span><span className="badge">용신: {finalResult.yongshin}</span></p></div>}
              <div className="actions"><button className="ghost" onClick={() => setActiveStep(2)}>이전</button><button onClick={saveCase}>{saving ? "저장 중..." : "Save Case + Regression"}</button></div>
            </>
          ) : (
            <p className="muted">먼저 Preview를 생성하세요.</p>
          )}

          {saveResult && (
            <div className="card compact">
              <h3>저장 결과</h3>
              <p>
                <span className={`badge ${saveResult.saved ? "good" : "bad"}`}>saved: {String(saveResult.saved)}</span>
                <span className="badge info">path: {saveResult.path ?? "-"}</span>
                <span className={`badge ${singlePassed === true ? "good" : singlePassed === false ? "bad" : "warn"}`}>single case: {String(singlePassed ?? "-")}</span>
                <span className={`badge ${regressionFailed === 0 ? "good" : regressionFailed ? "bad" : "warn"}`}>regression failed: {String(regressionFailed ?? "-")}</span>
              </p>
              <details><summary>저장/회귀검증 상세 JSON</summary><pre>{JSON.stringify(saveResult, null, 2)}</pre></details>
              {saveResult.saved && <p><Link href={`/cases/${encodeURIComponent(saveResult.case_id ?? caseId)}`}>저장된 케이스 보기 →</Link></p>}
            </div>
          )}
        </section>
      )}

      {preview && (
        <section className="card">
          <h2>Preview Detail</h2>
          <details open><summary>Linked Rules</summary><pre>{JSON.stringify(preview.linked_rules, null, 2)}</pre></details>
          <details><summary>Rule Improvement Candidates</summary><pre>{JSON.stringify(preview.rule_improvement_candidates, null, 2)}</pre></details>
          <details><summary>Raw YAML</summary><pre>{preview.raw_yaml}</pre></details>
          <details><summary>Engine Result JSON</summary><pre>{JSON.stringify(preview.engine_result, null, 2)}</pre></details>
        </section>
      )}
    </main>
  );
}
