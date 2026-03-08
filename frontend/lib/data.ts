import { Article, Cluster } from "./types";

const isStatic = process.env.NEXT_PUBLIC_STATIC_MODE === "true";
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

async function getJson<T>(path: string): Promise<T> {
  const apiBase = isStatic ? "" : "http://localhost:8000";
  const prefix = isStatic ? basePath : "";
  const res = await fetch(`${apiBase}${prefix}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`failed ${path}`);
  return res.json();
}

export async function loadFeed(): Promise<{ items: Article[]; fallback: boolean }> {
  const feed = await getJson<{ items: Article[] }>(isStatic ? "/data/feed.json" : "/api/feed");
  return { items: feed.items || [], fallback: isStatic };
}

export async function loadArticle(id: string): Promise<Article> {
  return getJson<Article>(isStatic ? `/data/articles/${id}.json` : `/api/articles/${id}`);
}

export async function loadClusters(): Promise<Cluster[]> {
  return getJson<Cluster[]>(isStatic ? "/data/clusters.json" : "/api/clusters");
}

export async function loadTrends(): Promise<any> {
  return getJson<any>(isStatic ? "/data/trends.json" : "/api/trends");
}
