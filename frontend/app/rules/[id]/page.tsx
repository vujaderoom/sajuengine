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

type SimulationResult = {
  rule_version: string;
  fired: boolean;
  condition_eval: {
    result: boolean;
    mode?: string;
    items: Array<{
      condition: string;
      left: string;
      operator: string;
      right: unknown;
      actual: unknown;
      result: boolean;
      error?: string;
    }>;
  };
  proposal_preview: unknown;
  chart_result: unknown;
  facts: unknown;
};

export default function RuleDetailPage({ params }: { params: { id: string } }) {
  const [rule, setRule] = useState<RuleDetail | null>(null);
  const [simulation, setSimulation] = useState<SimulationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [simError, setSimError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [simLoading, setSimLoading] = useState(false);

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

  async function simulateRule() {
    setSimLoading(true);
    setSimError(null);
    try {
      const res = await fetch(`/api/rules/${encodeURIComponent(params.id)}/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const json = await res.json();
      if (!res.ok) {
        throw new Error(json?.detail ?? json?.message ?? `API error: ${res.status}`);
      }
      setSimulation(json);
    } catch (err) {
      setSimError(err instanceof Error ? err.message : "unknown error");
    } finally {
      setSimLoading(false);
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
        <button onClick={loadRule}>{loading ? "불러오는 중..." : "Rule 새로고침"}</button>{" "}
        <button onClick={simulateRule}>{simLoading ? "시뮬레이션 중..." : "현재 샘플 Fact로 시뮬레이션"}</button>
      </div>

      {error && (
        <div className="card">
          <h2>Error</h2>
          <p style={{ color: "#fca5a5" }}>{error}</p>
        </div>
      )}

      {simError && (
        <div className="card">
          <h2>Simulation Error</h2>
          <p style={{ color: "#fca5a5" }}>{simError}</p>
        </div>
      )}

      {simulation && (
        <div className="card">
          <h2>Simulation Result</h2>
          <p>
            <span className="badge">fired: {String(simulation.fired)}</span>
            <span className="badge">mode: {simulation.condition_eval?.mode ?? "none"}</span>
            <span className="badge">result: {String(simulation.condition_eval?.result)}</span>
          </p>
          <h3>Condition Evaluation</h3>
          {simulation.condition_eval?.items?.map((item, index) => (
            <div className="card" key={`${item.condition}-${index}`}>
              <p>
                <strong>{item.condition}</strong>
              </p>
              <p>
                <span className="badge">actual: {JSON.stringify(item.actual)}</span>
                <span className="badge">expected: {JSON.stringify(item.right)}</span>
                <span className="badge">operator: {item.operator}</span>
                <span className="badge">result: {String(item.result)}</span>
              </p>
              {item.error && <p style={{ color: "#fca5a5" }}>{item.error}</p>}
            </div>
          ))}
          <h3>Proposal Preview</h3>
          <pre>{JSON.stringify(simulation.proposal_preview, null, 2)}</pre>
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
