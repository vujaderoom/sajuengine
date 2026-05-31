"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type LogicCardSummary = {
  id: string;
  title: string;
  category: string;
  status: string;
  active: boolean;
  original_text: string;
  tags: string[];
  path: string;
  updated_at?: string;
};

function statusBadge(status: string, active: boolean) {
  if (active || status === "active") return "good";
  if (status === "disabled") return "bad";
  if (status === "reviewed" || status === "structured") return "warn";
  return "info";
}

export default function LogicPage() {
  const [cards, setCards] = useState<LogicCardSummary[]>([]);
  const [selected, setSelected] = useState<any>(null);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [includeDisabled, setIncludeDisabled] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadCards() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/logic-cards?include_disabled=${includeDisabled}`, { cache: "no-store" });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.message ?? `API ${res.status}`);
      setCards(data.cards ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function loadDetail(id: string) {
    const res = await fetch(`/api/logic-cards/${encodeURIComponent(id)}`, { cache: "no-store" });
    const data = await res.json();
    if (res.ok) setSelected(data);
  }

  async function toggle(id: string, active: boolean) {
    setLoading(true);
    try {
      const res = await fetch(`/api/logic-cards/${encodeURIComponent(id)}/toggle`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ active }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.message ?? `API ${res.status}`);
      await loadCards();
      if (selected?.id === id) await loadDetail(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function deleteCard(id: string) {
    if (!confirm("이 Logic Card를 삭제할까요?")) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/logic-cards/${encodeURIComponent(id)}`, { method: "DELETE" });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.message ?? `API ${res.status}`);
      setSelected(null);
      await loadCards();
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCards();
  }, [includeDisabled]);

  const categories = useMemo(() => ["all", ...Array.from(new Set(cards.map((c) => c.category).filter(Boolean)))], [cards]);
  const filtered = cards.filter((card) => {
    const text = `${card.title} ${card.original_text} ${card.tags?.join(" ")}`.toLowerCase();
    const okQuery = !query || text.includes(query.toLowerCase());
    const okCategory = category === "all" || card.category === category;
    return okQuery && okCategory;
  });

  return (
    <main>
      <section className="page-hero">
        <div className="card">
          <h1 className="hero-title">Logic Library</h1>
          <p className="hero-subtitle">문장형 명리 지식을 원문 그대로 저장하고, AI 구조화 결과를 검토한 뒤 문장별로 active/disabled를 관리합니다.</p>
          <div className="summary-strip"><span className="badge info">I-3</span><span className="badge info">문장 지식 DB</span><span className="badge warn">active만 매칭 사용</span></div>
        </div>
        <div className="card compact"><h2>빠른 작업</h2><Link href="/logic/new"><button>새 문장 등록</button></Link><p>{loading && <span className="badge warn">로딩 중</span>}<span className="badge info">총 {cards.length}개</span></p>{error && <p style={{ color: "#b91c1c" }}>Error: {error}</p>}</div>
      </section>

      <section className="card">
        <h2>검색/필터</h2>
        <div className="grid-3">
          <label>검색<input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="무토, 화다, 도화..." /></label>
          <label>카테고리<select value={category} onChange={(e) => setCategory(e.target.value)}>{categories.map((c) => <option key={c} value={c}>{c}</option>)}</select></label>
          <label>비활성 포함<select value={includeDisabled ? "yes" : "no"} onChange={(e) => setIncludeDisabled(e.target.value === "yes")}><option value="yes">포함</option><option value="no">active만</option></select></label>
        </div>
      </section>

      <section className="grid" style={{ gridTemplateColumns: "420px 1fr" }}>
        <div className="card">
          <h2>문장 목록</h2>
          <div className="stack">
            {filtered.map((card) => (
              <div className="card compact" key={card.id} style={{ boxShadow: "none" }}>
                <p><strong>{card.title}</strong></p>
                <p className="muted">{card.original_text}</p>
                <p><span className={`badge ${statusBadge(card.status, card.active)}`}>{card.active ? "active" : card.status}</span><span className="badge info">{card.category}</span>{card.tags?.slice(0, 3).map((t) => <span className="badge" key={t}>{t}</span>)}</p>
                <div className="summary-strip"><button onClick={() => loadDetail(card.id)}>상세</button><button onClick={() => toggle(card.id, !card.active)}>{card.active ? "disable" : "active"}</button><button onClick={() => deleteCard(card.id)}>삭제</button></div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          {!selected && <p className="muted">왼쪽에서 문장을 선택하세요.</p>}
          {selected && (
            <>
              <h2>{selected.title}</h2>
              <p className="summary-strip"><span className={`badge ${statusBadge(selected.status, selected.active)}`}>{selected.active ? "active" : selected.status}</span><span className="badge info">{selected.category}</span><span className="badge">{selected.id}</span></p>
              <div className="card compact"><h3>원문</h3><p>{selected.original_text}</p></div>
              <div className="grid">
                <div className="card compact"><h3>조건</h3><pre>{JSON.stringify(selected.structured?.conditions, null, 2)}</pre></div>
                <div className="card compact"><h3>효과</h3><pre>{JSON.stringify(selected.structured?.effect, null, 2)}</pre></div>
              </div>
              <div className="card compact"><h3>해석/주의</h3><p>{selected.structured?.interpretation?.normalized_summary}</p><p>{selected.structured?.caution?.notes?.map((x: string, i: number) => <span className="badge warn" key={i}>{x}</span>)}</p></div>
              <details><summary>Raw YAML</summary><pre>{selected._raw_yaml}</pre></details>
            </>
          )}
        </div>
      </section>
    </main>
  );
}
