"use client";

import Link from "next/link";
import { useState } from "react";

type PreviewResponse = {
  case_id: string;
  chart_result: unknown;
  engine_result: unknown;
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
  single_case_result?: unknown;
  regression_result?: unknown;
  preview?: PreviewResponse;
};

export default function NewCasePage() {
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
    birth: {
      name,
      sex,
      birth_datetime: birthDatetime,
      calendar_type: "solar",
      timezone: "Asia/Seoul",
      location: "Seoul",
    },
    image_logic_text: imageLogicText,
    disease_core: diseaseCore,
    disease_subtype: diseaseSubtype,
    disease_reason: diseaseReason,
    medicine_type: medicineType,
    medicine_action: medicineAction,
    medicine_reason: medicineReason,
    yongshin_primary: yongshinPrimary,
    yongshin_symbols: yongshinSymbolsText
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean),
    excluded_candidates: [],
    notes: notesText
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean),
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
    const symbols = Array.isArray(payload.yongshin_symbols) ? payload.yongshin_symbols.join(", ") : yongshinSymbolsText;
    setYongshinSymbolsText(symbols);
    const notes = Array.isArray(payload.notes) ? payload.notes.join("\n") : notesText;
    setNotesText(notes);
  }

  async function structureNaturalLogic() {
    setStructuring(true);
    setError(null);
    setSaveResult(null);
    try {
      const res = await fetch("/api/cases/authoring/structure-natural-logic", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          case_id: caseId,
          title,
          birth: authoringPayload.birth,
          natural_logic_text: naturalLogicText,
        }),
      });
      const json = await res.json();
      if (!res.ok) {
        throw new Error(json?.message ?? `API error: ${res.status}`);
      }
      setStructured(json);
      setPreview(json.preview);
      applyStructuredAuthoring(json.structured_authoring);
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
      if (!res.ok) {
        throw new Error(json?.message ?? `API error: ${res.status}`);
      }
      setPreview(json);
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
        body: JSON.stringify({
          authoring: authoringPayload,
          overwrite: false,
          run_regression_after_save: true,
        }),
      });
      const json = await res.json();
      if (!res.ok) {
        throw new Error(json?.message ?? `API error: ${res.status}`);
      }
      setSaveResult(json);
      if (json.preview) setPreview(json.preview);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main>
      <div className="card">
        <h1>New Case Authoring</h1>
        <p>사주 해석 논리를 Case YAML 초안으로 변환하고 기존 룰 연결 후보를 확인합니다.</p>
        <p>
          <Link href="/cases">← Case Ledger</Link>{" | "}
          <Link href="/governance">Rule Governance</Link>
        </p>
      </div>

      <div className="card">
        <h2>Case Meta</h2>
        <label>
          Case ID
          <input value={caseId} onChange={(event) => setCaseId(event.target.value)} />
        </label>
        <label>
          Title
          <input value={title} onChange={(event) => setTitle(event.target.value)} />
        </label>
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
          <input value={birthDatetime} onChange={(event) => setBirthDatetime(event.target.value)} />
        </label>
      </div>

      <div className="card">
        <h2>Natural Logic Structuring</h2>
        <p>자연어 물상 설명을 입력하면 구조화 초안을 생성합니다. 현재는 규칙 기반 scaffold입니다.</p>
        <label>
          Natural Logic Text
          <textarea value={naturalLogicText} onChange={(event) => setNaturalLogicText(event.target.value)} rows={8} />
        </label>
        <button onClick={structureNaturalLogic}>{structuring ? "구조화 중..." : "물상 논리 자동 구조화"}</button>
      </div>

      {structured && (
        <div className="card">
          <h2>Structured Extraction Notes</h2>
          <pre>{JSON.stringify({ confidence: structured.confidence, extraction_notes: structured.extraction_notes }, null, 2)}</pre>
        </div>
      )}

      <div className="card">
        <h2>Interpretation Logic</h2>
        <label>
          Image Logic
          <textarea value={imageLogicText} onChange={(event) => setImageLogicText(event.target.value)} rows={8} />
        </label>
        <label>
          Disease Core
          <input value={diseaseCore} onChange={(event) => setDiseaseCore(event.target.value)} />
        </label>
        <label>
          Disease Subtype
          <input value={diseaseSubtype} onChange={(event) => setDiseaseSubtype(event.target.value)} />
        </label>
        <label>
          Disease Reason
          <textarea value={diseaseReason} onChange={(event) => setDiseaseReason(event.target.value)} rows={3} />
        </label>
        <label>
          Medicine Type
          <input value={medicineType} onChange={(event) => setMedicineType(event.target.value)} />
        </label>
        <label>
          Medicine Action
          <input value={medicineAction} onChange={(event) => setMedicineAction(event.target.value)} />
        </label>
        <label>
          Medicine Reason
          <textarea value={medicineReason} onChange={(event) => setMedicineReason(event.target.value)} rows={3} />
        </label>
        <label>
          Yongshin Primary
          <input value={yongshinPrimary} onChange={(event) => setYongshinPrimary(event.target.value)} />
        </label>
        <label>
          Yongshin Symbols, comma separated
          <input value={yongshinSymbolsText} onChange={(event) => setYongshinSymbolsText(event.target.value)} />
        </label>
        <label>
          Notes
          <textarea value={notesText} onChange={(event) => setNotesText(event.target.value)} rows={4} />
        </label>
        <button onClick={generatePreview}>{loading ? "생성 중..." : "Case YAML Preview 생성"}</button>{" "}
        <button onClick={saveCase}>{saving ? "저장 중..." : "Save Case + Regression"}</button>
      </div>

      {error && (
        <div className="card">
          <h2>Error</h2>
          <p style={{ color: "#fca5a5" }}>{error}</p>
        </div>
      )}

      {saveResult && (
        <div className="card">
          <h2>Save Result</h2>
          <p>
            <span className="badge">saved: {String(saveResult.saved)}</span>
            <span className="badge">path: {saveResult.path ?? "-"}</span>
            <span className="badge">reason: {saveResult.reason ?? "-"}</span>
          </p>
          <pre>{JSON.stringify({ single_case_result: saveResult.single_case_result, regression_result: saveResult.regression_result }, null, 2)}</pre>
        </div>
      )}

      {preview && (
        <>
          <div className="card">
            <h2>Generated Preview</h2>
            <p>
              <span className="badge">case_id: {preview.case_id}</span>
              <span className="badge">linked_rules: {preview.linked_rules.length}</span>
              <span className="badge">improvements: {preview.rule_improvement_candidates.length}</span>
            </p>
            <pre>{preview.save_instruction}</pre>
          </div>

          <div className="card">
            <h2>Linked Rules</h2>
            <pre>{JSON.stringify(preview.linked_rules, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Rule Improvement Candidates</h2>
            <pre>{JSON.stringify(preview.rule_improvement_candidates, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Raw YAML</h2>
            <pre>{preview.raw_yaml}</pre>
          </div>

          <div className="card">
            <h2>Engine Result</h2>
            <pre>{JSON.stringify(preview.engine_result, null, 2)}</pre>
          </div>
        </>
      )}
    </main>
  );
}
