"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type CaseSummary = {
  id: string;
  title: string;
  status: string;
  version: string;
  path: string;
  birth: {
    name?: string;
    sex?: string;
    birth_datetime?: string;
    calendar_type?: string;
    timezone?: string;
    location?: string;
  };
  chart: {
    year?: string;
    month?: string;
    day?: string;
    hour?: string;
  };
  pillar_text: string;
  interpretation_summary: {
    core_disease?: string;
    derived_diseases?: string[];
    medicine?: string;
    yongshin?: string;
    yongshin_symbols?: string[];
    selected_yongshin_source_rule?: string;
    water_is_waterlogged?: boolean;
    water_needs_drying?: boolean;
    preferred_element?: string;
    primary_action?: string;
  };
  notes: string[];
};

type CasesResponse = {
  cases: CaseSummary[];
};

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
        item.interpretation_summary?.medicine,
        item.interpretation_summary?.yongshin,
        item.interpretation_summary?.selected_yongshin_source_rule,
        ...(item.interpretation_summary?.yongshin_symbols ?? []),
        ...(item.notes ?? []),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return haystack.includes(q);
    });
  }, [data, query]);

  return (
    <main>
      <div className="card">
        <h1>Case Ledger</h1>
        <p>Golden Case가 어떤 원국과 어떤 해석 논리로 저장됐는지 관리하는 화면입니다.</p>
        <p>
          <Link href="/dashboard">← Dashboard</Link>{" | "}
          <Link href="/rules">Rule Studio</Link>{" | "}
          <Link href="/regressions">Regression Runner</Link>
        </p>
        <button onClick={loadCases}>{loading ? "불러오는 중..." : "Cases 새로고침"}</button>
      </div>

      <div className="card">
        <h2>Search</h2>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="GC-001, 己亥, 火, 침수형, 말림 등"
        />
        <p>
          <span className="badge">total: {data?.cases.length ?? 0}</span>
          <span className="badge">shown: {filtered.length}</span>
        </p>
      </div>

      {error && (
        <div className="card">
          <h2>Error</h2>
          <p style={{ color: "#fca5a5" }}>{error}</p>
        </div>
      )}

      {filtered.map((item) => (
        <div className="card" key={item.id}>
          <h2>
            <Link href={`/cases/${encodeURIComponent(item.id)}`}>{item.id}</Link>
          </h2>
          <p>{item.title}</p>
          <p>
            <span className="badge">status: {item.status}</span>
            <span className="badge">version: {item.version}</span>
            <span className="badge">birth: {item.birth?.birth_datetime}</span>
          </p>
          <p>
            <span className="badge">원국: {item.pillar_text || "미지정"}</span>
          </p>
          <p>
            <span className="badge">핵심 병: {item.interpretation_summary?.core_disease ?? "미지정"}</span>
            <span className="badge">약: {item.interpretation_summary?.medicine ?? "미지정"}</span>
            <span className="badge">용신: {item.interpretation_summary?.yongshin ?? "미지정"}</span>
          </p>
          {item.interpretation_summary?.yongshin_symbols?.length ? (
            <p>
              <span className="badge">세부 후보: {item.interpretation_summary.yongshin_symbols.join(", ")}</span>
            </p>
          ) : null}
          {item.notes?.length ? <pre>{item.notes.join("\n")}</pre> : null}
          <p>
            <Link href={`/cases/${encodeURIComponent(item.id)}`}>상세 보기 →</Link>
          </p>
        </div>
      ))}
    </main>
  );
}
