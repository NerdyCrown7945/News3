import { loadTrends } from "../../lib/data";

function bar(n: number) {
  return "█".repeat(Math.min(30, n));
}

export default async function TrendsPage() {
  const trends = await loadTrends();
  return (
    <section>
      <h2>최근 {trends.recent_days}일 트렌드</h2>
      <h3>키워드 Top</h3>
      <ul>{trends.keywords_top?.map((k: any) => <li key={k.keyword}>{k.keyword} {bar(k.count)} ({k.count})</li>)}</ul>
      <h3>소스 비율</h3>
      <ul>{trends.source_distribution?.map((s: any) => <li key={s.source}>{s.source} {bar(s.count)} ({s.count})</li>)}</ul>
      <h3>AI vs SciTech</h3>
      <p>AI: {trends.topic_ratio?.AI ?? 0} / ScienceTech: {trends.topic_ratio?.ScienceTech ?? 0}</p>
    </section>
  );
}
