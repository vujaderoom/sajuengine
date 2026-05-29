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

export default function NewCasePage() {
  const [caseId, setCaseId] = useState("GC-DRAFT-001");
  const [title, setTitle] = useState("새 해석 케이스 초안");
  const [name, setName] = useState("draft");
  const [sex, setSex] = useState("unknown");
  const [birthDatetime, setBirthDatetime] = useState("1991-05-29T16:36:00");
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
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function generatePreview() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/cases/authoring/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
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
        }),
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
        <button onClick={generatePreview}>{loading ? "생성 중..." : "Case YAML Preview 생성"}</button>
      </div>

      {error && (
        <div className="card">
          <h2>Error</h2>
          <p style={{ color: "#fca5a5" }}>{error}</p>
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
