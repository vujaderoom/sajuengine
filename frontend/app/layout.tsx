import Link from "next/link";
import "./globals.css";

export const metadata = {
  title: "Saju Engine",
  description: "Rule Studio Dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <div className="app-shell">
          <header className="topbar">
            <Link className="brand" href="/dashboard">
              <strong>Saju Engine</strong>
              <span>Rule · Case · Logic · Report Workbench</span>
            </Link>
            <nav className="nav">
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/logic">Logic Library</Link>
              <Link href="/logic/new">New Logic</Link>
              <Link href="/cases">Cases</Link>
              <Link href="/cases/new">New Case</Link>
              <Link href="/rules">Rules</Link>
              <Link href="/rules/candidates">Rule Candidates</Link>
              <Link href="/governance">Governance</Link>
              <Link href="/regressions">Regression</Link>
              <Link href="/reports/preview">Report</Link>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
