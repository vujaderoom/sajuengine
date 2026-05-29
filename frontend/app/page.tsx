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
