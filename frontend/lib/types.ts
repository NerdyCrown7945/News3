export type Topic = "AI" | "ScienceTech" | "Other" | "All";

export interface Article {
  id: string;
  title: string;
  source_name: string;
  source_url: string;
  published_at: string;
  topic: Topic;
  canonical_url: string;
  original_url: string;
  is_valid_source_url: boolean;
  source_url_status_code?: number;
  summary_ko: string;
  key_points: string[];
  keywords: string[];
  cluster_id?: string;
}

export interface Cluster {
  cluster_id: string;
  cluster_title: string;
  cluster_summary_ko: string;
  keywords: string[];
  article_ids: string[];
  updated_at: string;
}
