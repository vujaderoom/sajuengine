"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type RuleSummary = {
  id: string;
  title: string;
  layer: string;
  target: string;
  priority: number;
  enabled: boolean;
  status: string;
  path: string;
};

type RulesResponse = {
  rule_version: string;
  rules: RuleSummary[];
};

export default function RulesPage() {
  const [data, setData] = useState<RulesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadRules() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/rules", { cache: "no-store" });
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
    loadRules();
  }, []);

  return (
    <main>
      <div className="card">
        <h1>Rule Studio</h1>
        <p>YAML Rule DSL 목록을 확인하는 내부 검증 화면입니다.</p>
        <p>
          <Link href="/dashboard">← Dashboard</Link>
        </p>
        <button onClick={loadRules}>{loading ? "불러오는 중..." : "Rules 새로고침"}</button>
      </div>

      {error && (
        <div className="card">
          <h2>Error</h2>
          <p style={{ color: "#fca5a5" }}>{error}</p>
        </div>
      )}

      {data && (
        <>
          <div className="card">
            <h2>Rule Version</h2>
            <p>
              <span className="badge">{data.rule_version}</span>
              <span className="badge">{data.rules.length} rules</span>
            </p>
          </div>

          {data.rules.map((rule) => (
            <div className="card" key={rule.id}>
              <h2>{rule.id}</h2>
              <p>{rule.title}</p>
              <p>
                <span className="badge">layer: {rule.layer}</span>
                <span className="badge">target: {rule.target}</span>
                <span className="badge">priority: {rule.priority}</span>
                <span className="badge">enabled: {String(rule.enabled)}</span>
                <span className="badge">status: {rule.status}</span>
              </p>
              <pre>{rule.path}</pre>
            </div>
          ))}
        </>
      )}
    </main>
  );
}
