"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type CaseDetail = {
  id: string;
  title: string;
  status: string;
  version: string;
  path: string;
  birth: Record<string, unknown>;
  chart: Record<string, unknown>;
  pillar_text: string;
  expected: Record<string, unknown>;
  interpretation_summary: Record<string, unknown>;
  notes: string[];
  raw_yaml: string;
};

export default function CaseDetailPage({ params }: { params: { id: string } }) {
  const [item, setItem] = useState<CaseDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadCase() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/case-detail/${encodeURIComponent(params.id)}`, {
        cache: "no-store",
      });
      const json = await res.json();
      if (!res.ok) {
        throw new Error(json?.detail ?? json?.message ?? `API error: ${res.status}`);
      }
      setItem(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCase();
  }, [params.id]);

  return (
    <main>
      <div className="card">
        <h1>Case Detail</h1>
        <p>
          <Link href="/cases">← Case Ledger</Link>{" | "}
          <Link href="/regressions">Regression Runner</Link>
        </p>
        <button onClick={loadCase}>{loading ? "불러오는 중..." : "Case 새로고침"}</button>
      </div>

      {error && (
        <div className="card">
          <h2>Error</h2>
          <p style={{ color: "#fca5a5" }}>{error}</p>
        </div>
      )}

      {item && (
        <>
          <div className="card">
            <h2>{item.id}</h2>
            <p>{item.title}</p>
            <p>
              <span className="badge">status: {item.status}</span>
              <span className="badge">version: {item.version}</span>
              <span className="badge">path: {item.path}</span>
            </p>
            <p>
              <span className="badge">원국: {item.pillar_text || "미지정"}</span>
            </p>
          </div>

          <div className="card">
            <h2>Birth</h2>
            <pre>{JSON.stringify(item.birth, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Interpretation Summary</h2>
            <pre>{JSON.stringify(item.interpretation_summary, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Notes / Logic</h2>
            <pre>{item.notes?.join("\n")}</pre>
          </div>

          <div className="card">
            <h2>Expected</h2>
            <pre>{JSON.stringify(item.expected, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Raw YAML</h2>
            <pre>{item.raw_yaml}</pre>
          </div>
        </>
      )}
    </main>
  );
}
