"use client";

import Link from "next/link";
import { useState } from "react";

const sample = "무토일간이 화가 많으면 술, 여자를 좋아한다.";

export default function NewLogicPage() {
  const [originalText, setOriginalText] = useState(sample);
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("auto");
  const [active, setActive] = useState(false);
  const [structured, setStructured] = useState<any>(null);
  const [saved, setSaved] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function structure() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/logic-cards/structure", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ original_text: originalText, title, category, source: "user" }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.message ?? `API ${res.status}`);
      setStructured(data.structured);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function save() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/logic-cards", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ original_text: originalText, title: title || structured?.title || "", category, status: active ? "active" : "structured", active, source: "user", tags: structured?.effect?.tags ?? [], structured }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.message ?? `API ${res.status}`);
      setSaved(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <section className="page-hero">
        <div className="card">
          <h1 className="hero-title">새 Logic Card</h1>
          <p className="hero-subtitle">문장으로 지식을 입력하면 앱이 조건·해석·효과·주의사항으로 구조화합니다. 원문은 그대로 보존됩니다.</p>
          <div className="summary-strip"><span className="badge info">문장 입력</span><span className="badge info">구조화</span><span className="badge warn">직접 active 선택</span></div>
        </div>
        <div className="card compact"><h2>이동</h2><Link href="/logic"><button>Logic Library</button></Link>{loading && <p><span className="badge warn">처리 중</span></p>}{error && <p style={{ color: "#b91c1c" }}>Error: {error}</p>}</div>
      </section>

      <section className="grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
        <div className="card">
          <h2>1. 문장 입력</h2>
          <label>제목<input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="비워두면 자동 생성" /></label>
          <label>카테고리<select value={category} onChange={(e) => setCategory(e.target.value)}><option value="auto">auto</option><option value="일간별 성향">일간별 성향</option><option value="병약용신">병약용신</option><option value="십성">십성</option><option value="합충형파">합충형파</option><option value="신살/공망">신살/공망</option><option value="대운/세운">대운/세운</option><option value="일반 명리 문장">일반 명리 문장</option></select></label>
          <label>원문<textarea value={originalText} onChange={(e) => setOriginalText(e.target.value)} rows={8} /></label>
          <label>저장 상태<select value={active ? "active" : "structured"} onChange={(e) => setActive(e.target.value === "active")}><option value="structured">structured 저장</option><option value="active">바로 active</option></select></label>
          <div className="summary-strip"><button onClick={structure}>AI 구조화 Preview</button><button onClick={save} disabled={!structured}>저장</button></div>
          <p className="muted">권장: 먼저 structured로 저장하고, 검토 후 /logic에서 active로 켜세요.</p>
        </div>

        <div className="card">
          <h2>2. 구조화 Preview</h2>
          {!structured && <p className="muted">AI 구조화 Preview를 눌러 초안을 만드세요.</p>}
          {structured && (
            <>
              <p className="summary-strip"><span className="badge info">{structured.category}</span>{structured.effect?.tags?.map((t: string) => <span className="badge" key={t}>{t}</span>)}</p>
              <div className="card compact"><h3>정규화 해석</h3><p>{structured.interpretation?.normalized_summary}</p></div>
              <div className="grid"><div className="card compact"><h3>조건</h3><pre>{JSON.stringify(structured.conditions, null, 2)}</pre></div><div className="card compact"><h3>효과</h3><pre>{JSON.stringify(structured.effect, null, 2)}</pre></div></div>
              <div className="card compact"><h3>주의사항</h3><p>{structured.caution?.notes?.map((x: string, i: number) => <span className="badge warn" key={i}>{x}</span>)}</p></div>
            </>
          )}
          {saved && <div className="card compact"><h3>저장 완료</h3><p><span className="badge good">saved</span><span className="badge info">{saved.card?.id}</span><span className="badge">{saved.path}</span></p><Link href="/logic"><button>목록에서 보기</button></Link></div>}
        </div>
      </section>
    </main>
  );
}
