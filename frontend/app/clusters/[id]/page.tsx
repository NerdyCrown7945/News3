import Link from "next/link";
import { loadClusters, loadFeed } from "../../../lib/data";

export default async function ClusterDetail({ params }: { params: { id: string } }) {
  const [clusters, feed] = await Promise.all([loadClusters(), loadFeed()]);
  const cluster = clusters.find((c) => c.cluster_id === params.id);
  if (!cluster) return <p>클러스터를 찾을 수 없습니다.</p>;
  const related = feed.items.filter((a) => cluster.article_ids.includes(a.id));
  return (
    <section>
      <h2>{cluster.cluster_title}</h2>
      <p>{cluster.cluster_summary_ko}</p>
      <ul>{related.map((a) => <li key={a.id}><Link href={`/articles/${a.id}`}>{a.title}</Link></li>)}</ul>
    </section>
  );
}
