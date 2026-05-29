from pathlib import Path

def w(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.lstrip(), encoding="utf-8")

w("package.json", '''
{
  "name": "sajuengine",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "backend": "cd backend && python -m venv .venv && . .venv/bin/activate && pip install -e . && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
    "dev": "npm --prefix frontend install && npm --prefix frontend run dev -- --host 0.0.0.0"
  }
}
''')

w("backend/pyproject.toml", '''
[project]
name = "sajuengine-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic>=2.8.0"
]
''')

w("backend/app/main.py", '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI(title="Saju Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RuleRunnerRequest(BaseModel):
    rule_version: str = "v1.0.0"

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "sajuengine"}

@app.get("/api/v1/rule-runner/sample")
def sample():
    return execute_rule_runner()

@app.post("/api/v1/rule-runner/execute")
def execute(_: RuleRunnerRequest):
    return execute_rule_runner()

def execute_rule_runner():
    fact = {
        "chart": {"year": "辛未", "month": "癸巳", "day": "己亥", "hour": "壬申"},
        "raw": {"HeatScore": 2, "MoistureScore": -1, "EWMScore": 1},
        "display": {"HeatIndex": 83, "MoistureIndex": 33, "EWMIndex": 25},
        "flow": {"blocked": True, "support_path": "weak_or_broken"},
        "binding": {"CI": 2, "BindingStrength": 3, "bindings": ["巳亥沖", "巳申合"]},
        "storage": {"root_support": 1, "base_stability": "weak"},
        "climate": {"season": "巳月", "temperature": "hot", "humidity": "dry"}
    }

    proposals = [
        {
            "proposal_id": "prop_flow_001",
            "candidate_type": "core_disease",
            "value": "유통 차단형 병",
            "score_delta": 2.0,
            "source_rule": "disease.flow.blocked.001",
            "reason": "생극 흐름이 결속이나 고립으로 막혀 유통 차단형 병 후보가 됩니다.",
            "evidence_query": {"tags": ["유통", "차단", "생극", "합충", "결속"]}
        },
        {
            "proposal_id": "prop_medicine_001",
            "candidate_type": "medicine",
            "value": "유통 개통형",
            "score_delta": 2.0,
            "source_rule": "medicine.flow.opening.001",
            "reason": "흐름이 막힌 구조를 여는 약 후보입니다.",
            "evidence_query": {"tags": ["약", "유통", "개통"]}
        },
        {
            "proposal_id": "prop_yongshin_001",
            "candidate_type": "yongshin",
            "value": "庚",
            "score_delta": 2.0,
            "source_rule": "yongshin.flow.metal.001",
            "reason": "유통 개통형 약의 실행 상징으로 庚을 용신 후보로 제안합니다.",
            "evidence_query": {"tags": ["용신", "庚", "금", "유통"]}
        }
    ]

    counter = {
        "rule_id": "counter.flow.open_path.001",
        "target_proposal": "prop_flow_001",
        "applied": False,
        "score_delta": 0.0,
        "reason": "support_path가 open이 아니므로 감점하지 않습니다."
    }

    final_result = {
        "core_disease": "유통 차단형 병",
        "derived_diseases": ["기후형 병"],
        "medicine": "유통 개통형",
        "yongshin": "庚",
        "secondary_yongshin": ["壬"],
        "depth": 2,
        "stability_grade": "B",
        "confidence": 0.86
    }

    decision_trace = [
        {"type": "FACT_BUILT", "stage": "fact_builder", "output_json": fact},
        {"type": "RULE_EVALUATED", "stage": "L2_PROPOSAL", "rule_id": "disease.flow.blocked.001", "fired": True},
        {"type": "PROPOSAL_CREATED", "stage": "L2_PROPOSAL", "proposal": proposals[0]},
        {"type": "COUNTER_RULE_APPLIED", "stage": "COUNTER_RULE", "counter_json": counter},
        {"type": "FINALIZED", "stage": "FINALIZER", "output_json": final_result}
    ]

    return {
        "execution_id": "ex_" + uuid4().hex[:12],
        "chart_id": "chart_" + uuid4().hex[:12],
        "rule_version": "v1.0.0",
        "facts": fact,
        "proposals": proposals,
        "counter_rules_applied": [counter],
        "final_result": final_result,
        "decision_trace": decision_trace
    }
''')

w("frontend/package.json", '''
{
  "name": "sajuengine-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "typescript": "^5.6.0",
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0"
  }
}
''')

w("frontend/next.config.mjs", '''
const nextConfig = {};
export default nextConfig;
''')

w("frontend/tsconfig.json", '''
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": false,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
''')

w("frontend/next-env.d.ts", '''
/// <reference types="next" />
/// <reference types="next/image-types/global" />
''')

w("frontend/app/layout.tsx", '''
import "./globals.css";

export const metadata = {
  title: "Saju Engine",
  description: "Rule Studio Dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
''')

w("frontend/app/globals.css", '''
body {
  margin: 0;
  background: #0f172a;
  color: #e5e7eb;
  font-family: Arial, Helvetica, sans-serif;
}

main {
  padding: 32px;
}

.card {
  border: 1px solid #334155;
  border-radius: 16px;
  background: #111827;
  padding: 20px;
  margin-bottom: 16px;
}

pre {
  white-space: pre-wrap;
  word-break: break-word;
  background: #020617;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 16px;
}

button {
  cursor: pointer;
  border: 0;
  border-radius: 10px;
  padding: 10px 16px;
  background: #38bdf8;
  color: #082f49;
  font-weight: 700;
}

.badge {
  display: inline-block;
  border: 1px solid #475569;
  border-radius: 999px;
  padding: 4px 10px;
  margin-right: 6px;
  color: #bae6fd;
}
''')

w("frontend/app/page.tsx", '''
import Link from "next/link";

export default function HomePage() {
  return (
    <main>
      <div className="card">
        <h1>Saju Engine</h1>
        <p>명리 판단 로직 워크벤치 초기 화면입니다.</p>
        <Link href="/dashboard">Dashboard 열기</Link>
      </div>
    </main>
  );
}
''')

w("frontend/app/dashboard/page.tsx", '''
"use client";

import { useState } from "react";

export default function DashboardPage() {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function runEngine() {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/rule-runner/execute", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({rule_version: "v1.0.0"})
      });
      setResult(await res.json());
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <div className="card">
        <h1>Rule Studio Dashboard MVP</h1>
        <p>Rule Runner → Proposal → Counter Rule → Finalizer → Decision Trace 흐름 검증 화면입니다.</p>
        <button onClick={runEngine}>{loading ? "실행 중..." : "Rule Runner 실행"}</button>
      </div>

      {result && (
        <>
          <div className="card">
            <h2>Finalizer 결과</h2>
            <p><span className="badge">핵심 병: {result.final_result.core_disease}</span></p>
            <p><span className="badge">약: {result.final_result.medicine}</span></p>
            <p><span className="badge">용신: {result.final_result.yongshin}</span></p>
            <p>Depth: {result.final_result.depth}</p>
            <p>Confidence: {result.final_result.confidence}</p>
          </div>

          <div className="card"><h2>Fact JSON</h2><pre>{JSON.stringify(result.facts, null, 2)}</pre></div>
          <div className="card"><h2>Proposals</h2><pre>{JSON.stringify(result.proposals, null, 2)}</pre></div>
          <div className="card"><h2>Decision Trace</h2><pre>{JSON.stringify(result.decision_trace, null, 2)}</pre></div>
        </>
      )}
    </main>
  );
}
''')

w(".gitignore", '''
backend/.venv/
backend/*.egg-info/
**/__pycache__/
frontend/node_modules/
frontend/.next/
.env
''')

print("created")
