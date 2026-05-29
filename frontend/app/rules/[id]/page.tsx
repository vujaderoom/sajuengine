"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type RuleDetail = {
  rule_version: string;
  id: string;
  title: string;
  layer: string;
  target: string;
  priority: number;
  enabled: boolean;
  status: string;
  path: string;
  when: unknown;
  then: unknown;
  score: unknown;
  counter_rules: unknown[];
  explain: unknown;
  evidence_query: unknown;
  raw_yaml: string;
};

export default function RuleDetailPage({ params }: { params: { id: string } }) {
  const [rule, setRule] = useState<RuleDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadRule() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/rules/${encodeURIComponent(params.id)}`, {
        cache: "no-store",
      });
      const json = await res.json();
      if (!res.ok) {
        throw new Error(json?.detail ?? json?.message ?? `API error: ${res.status}`);
      }
      setRule(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRule();
  }, [params.id]);

  return (
    <main>
      <div className="card">
        <h1>Rule Detail</h1>
        <p>
          <Link href="/rules">← Rule Studio</Link>
        </p>
        <button onClick={loadRule}>{loading ? "불러오는 중..." : "Rule 새로고침"}</button>
      </div>

      {error && (
        <div className="card">
          <h2>Error</h2>
          <p style={{ color: "#fca5a5" }}>{error}</p>
        </div>
      )}

      {rule && (
        <>
          <div className="card">
            <h2>{rule.id}</h2>
            <p>{rule.title}</p>
            <p>
              <span className="badge">version: {rule.rule_version}</span>
              <span className="badge">layer: {rule.layer}</span>
              <span className="badge">target: {rule.target}</span>
              <span className="badge">priority: {rule.priority}</span>
              <span className="badge">enabled: {String(rule.enabled)}</span>
              <span className="badge">status: {rule.status}</span>
            </p>
            <pre>{rule.path}</pre>
          </div>

          <div className="card">
            <h2>When</h2>
            <pre>{JSON.stringify(rule.when, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Then</h2>
            <pre>{JSON.stringify(rule.then, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Counter Rules</h2>
            <pre>{JSON.stringify(rule.counter_rules, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Evidence Query</h2>
            <pre>{JSON.stringify(rule.evidence_query, null, 2)}</pre>
          </div>

          <div className="card">
            <h2>Raw YAML</h2>
            <pre>{rule.raw_yaml}</pre>
          </div>
        </>
      )}
    </main>
  );
}
