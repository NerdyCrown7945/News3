"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { Article } from "../lib/types";

type Period = "24h" | "7d" | "30d" | "all";

function toMs(v: string) {
  return new Date(v).getTime();
}

function filterWithRelax(items: Article[], topic: string, period: Period, q: string) {
  const now = Date.now();
  const ranges: Record<Period, number> = { 24h: 24 * 3600e3, "7d": 7 * 24 * 3600e3, "30d": 30 * 24 * 3600e3, all: Infinity };
  const tries: Period[] = [period, "7d", "30d", "all"].filter((v, i, a) => a.indexOf(v as Period) === i) as Period[];
  for (const p of tries) {
    const r = items.filter((a) => {
      if (topic !== "All" && a.topic !== topic) return false;
      if (p !== "all" && now - toMs(a.published_at) > ranges[p]) return false;
      if (q && !(a.title + a.summary_ko).toLowerCase().includes(q.toLowerCase())) return false;
      return true;
    });
    if (r.length > 0) return { items: r, badge: p === period ? "" : `기간을 자동 확장했습니다: ${period} → ${p}` };
  }
  return { items: [], badge: "조건에 맞는 기사가 없습니다." };
}

export function NewsList({ items, fallback }: { items: Article[]; fallback: boolean }) {
  const [topic, setTopic] = useState("All");
  const [period, setPeriod] = useState<Period>("24h");
  const [query, setQuery] = useState("");
  const [order, setOrder] = useState("latest");

  const filtered = useMemo(() => {
    const { items: r, badge } = filterWithRelax(items, topic, period, query);
    const sorted = [...r].sort((a, b) => {
      const core = order === "latest" ? toMs(b.published_at) - toMs(a.published_at) : toMs(a.published_at) - toMs(b.published_at);
      if (core !== 0) return core;
      return `${a.source_name}:${a.title}:${a.id}`.localeCompare(`${b.source_name}:${b.title}:${b.id}`);
    });
    return { items: sorted, badge };
  }, [items, topic, period, query, order]);

  return (
    <section>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <select value={topic} onChange={(e) => setTopic(e.target.value)}><option>All</option><option>AI</option><option>ScienceTech</option></select>
        <select value={period} onChange={(e) => setPeriod(e.target.value as Period)}><option value="24h">24h</option><option value="7d">7d</option><option value="30d">30d</option><option value="all">all</option></select>
        <select value={order} onChange={(e) => setOrder(e.target.value)}><option value="latest">최신순</option><option value="oldest">오래된순</option></select>
        <input placeholder="검색" value={query} onChange={(e) => setQuery(e.target.value)} />
      </div>
      {fallback && <p style={{ color: "#a16207" }}>Static fallback mode</p>}
      <button disabled={fallback} title={fallback ? "정적 모드에서는 비활성" : "로컬 수집 실행"}>수집 실행</button>
      {!!filtered.badge && <p>{filtered.badge}</p>}
      {filtered.items.length === 0 ? <p>표시할 뉴스가 없습니다. 조건을 완화해보세요.</p> : null}
      <ul>
        {filtered.items.map((a) => (
          <li key={a.id} style={{ margin: "10px 0" }}>
            <Link href={`/articles/${a.id}`}>{a.title}</Link> <small>({a.source_name})</small>
            {a.cluster_id ? <small> · 이 이슈 관련 기사</small> : null}
          </li>
        ))}
      </ul>
    </section>
  );
}
