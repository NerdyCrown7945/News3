import Link from "next/link";
import { loadClusters } from "../../lib/data";

export default async function ClustersPage() {
  const clusters = await loadClusters();
  return (
    <section>
      <h2>Clusters</h2>
      <ul>
        {clusters.map((c) => (
          <li key={c.cluster_id}>
            <Link href={`/clusters/${c.cluster_id}`}>{c.cluster_title}</Link> · 이 이슈 관련 기사 {c.article_ids.length}개
          </li>
        ))}
      </ul>
    </section>
  );
}
