"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type CaseSummary = {
  id: string;
  title: string;
  status: string;
  version: string;
  path: string;
  birth: { birth_datetime?: string; sex?: string; name?: string };
  chart: { year?: string; month?: string; day?: string; hour?: string };
  pillar_text: string;
  interpretation_summary: {
    core_disease?: string;
    subtype?: string;
    medicine?: string;
    medicine_type?: string;
    yongshin?: string;
    yongshin_symbols?: string[];
    selected_yongshin_source_rule?: string;
    linked_rules?: string[];
  };
  notes: string[];
};

type CasesResponse = { cases: CaseSummary[] };

export default function CasesPage() {
  const [data, setData] = useState<CasesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");

  async function loadCases() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/cases", { cache: "no-store" });
      const json = await res.json();
      if (!res.ok) throw new Error(json?.message ?? `API error: ${res.status}`);
      setData(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCases();
  }, []);

  const filtered = useMemo(() => {
    const cases = data?.cases ?? [];
    const q = query.trim().toLowerCase();
    if (!q) return cases;
    return cases.filter((item) => {
      const haystack = [
        item.id,
        item.title,
        item.pillar_text,
        item.interpretation_summary?.core_disease,
        item.interpretation_summary?.subtype,
        item.interpretation_summary?.medicine,
        item.interpretation_summary?.medicine_type,
        item.interpretation_summary?.yongshin,
        item.interpretation_summary?.selected_yongshin_source_rule,
        ...(item.interpretation_summary?.yongshin_symbols ?? []),
        ...(item.interpretation_summary?.linked_rules ?? []),
        ...(item.notes ?? []),
      ].filter(Boolean).join(" ").toLowerCase();
      return haystack.includes(q);
    });
  }, [data, query]);

  return (
    <main>
      <section className="page-hero">
        <div className="card">
          <h1 className="hero-title">Case Ledger</h1>
          <p className="hero-subtitle">저장된 Golden Case를 병·약·용신 중심으로 관리합니다. 케이스가 쌓일수록 룰엔진이 단단해집니다.</p>
          <div className="summary-strip">
            <span className="badge info">total {data?.cases.length ?? 0}</span>
            <span className="badge info">shown {filtered.length}</span>
          </div>
        </div>
        <div className="card compact">
          <h2>빠른 작업</h2>
          <div className="actions">
            <Link href="/cases/new"><button>New Case</button></Link>
            <button className="ghost" onClick={loadCases}>{loading ? "불러오는 중..." : "새로고침"}</button>
          </div>
        </div>
      </section>

      <section className="card">
        <h2>검색</h2>
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="GC-001, 己亥, 火, 침수형, 말림 등" />
      </section>

      {error && <div className="card"><h2>Error</h2><p style={{ color: "#b91c1c" }}>{error}</p></div>}

      <section className="grid">
        {filtered.map((item) => (
          <article className="card" key={item.id}>
            <p>
              <span className={`badge ${item.status === "approved" ? "good" : "warn"}`}>{item.status}</span>
              <span className="badge info">{item.version}</span>
              <span className="badge">{item.birth?.birth_datetime}</span>
            </p>
            <h2><Link href={`/cases/${encodeURIComponent(item.id)}`}>{item.id}</Link></h2>
            <p className="muted">{item.title}</p>
            <div className="pillar-row">
              <div className="pillar"><small>년</small><strong>{item.chart.year ?? "-"}</strong></div>
              <div className="pillar"><small>월</small><strong>{item.chart.month ?? "-"}</strong></div>
              <div className="pillar"><small>일</small><strong>{item.chart.day ?? "-"}</strong></div>
              <div className="pillar"><small>시</small><strong>{item.chart.hour ?? "-"}</strong></div>
            </div>
            <div className="grid-3" style={{ marginTop: 14 }}>
              <div className="metric"><div className="metric-label">병</div><div className="metric-value">{item.interpretation_summary?.subtype ?? item.interpretation_summary?.core_disease ?? "-"}</div></div>
              <div className="metric"><div className="metric-label">약</div><div className="metric-value">{item.interpretation_summary?.medicine ?? "-"}</div></div>
              <div className="metric"><div className="metric-label">용신</div><div className="metric-value">{item.interpretation_summary?.yongshin ?? "-"}</div></div>
            </div>
            <p className="summary-strip">
              {(item.interpretation_summary?.yongshin_symbols ?? []).map((symbol) => <span className="badge" key={symbol}>{symbol}</span>)}
            </p>
            {item.interpretation_summary?.linked_rules?.length ? (
              <details>
                <summary>linked rules {item.interpretation_summary.linked_rules.length}</summary>
                <pre>{item.interpretation_summary.linked_rules.join("\n")}</pre>
              </details>
            ) : null}
            <p><Link href={`/cases/${encodeURIComponent(item.id)}`}>상세 보기 →</Link></p>
          </article>
        ))}
      </section>
    </main>
  );
}
