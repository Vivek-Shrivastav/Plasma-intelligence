const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Paper {
  id: string;
  arxiv_id: string | null;
  doi: string | null;
  title: string;
  authors: string[];
  journal: string | null;
  published_date: string;
  field: string | null;
  subfields: string[];
  importance_score: number | null;
  technical_depth: string | null;
  headline: string | null;
  short_summary: string | null;
  keywords: string[];
  concepts_detected: string[];
  figures: Figure[];
  pdf_url: string | null;
  paper_url: string | null;
  analysis: Analysis | null;
}

export interface Figure {
  url: string;
  description: string;
  index: number;
}

export interface Analysis {
  headline: string;
  short_summary: string;
  detailed_summary: string;
  field: string;
  subfield: string[];
  keywords: string[];
  concepts_detected: string[];
  technical_depth: string;
  key_contributions: string[];
  methods_used: string[];
  figures_explained: string[];
  open_problems: string[];
  literature_context: {
    historical_background: string;
    recent_trends: string;
    positioning: string;
  };
  classification_confidence: string;
  importance_score: number;
  tags: string[];
}

export interface Subfield {
  slug: string;
  name: string;
}

export interface LitReview {
  subfield: string;
  name: string;
  content_markdown: string;
  paper_count: number;
  last_updated: string | null;
  is_seeded: boolean;
}

export interface OpenProblemCluster {
  id: string;
  theme: string;
  description: string;
  subfields: string[];
  urgency: "high" | "medium" | "low";
  frequency: number;
  first_appeared: string | null;
  last_appeared: string | null;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`, { next: { revalidate: 300 } });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

export const api = {
  papers: {
    today: () => get<{ date: string; papers: Paper[] }>("/api/papers/today"),
    byDate: (d: string) => get<{ date: string; papers: Paper[] }>(`/api/papers/date/${d}`),
    byId: (id: string) => get<Paper>(`/api/papers/${id}`),
    list: (params?: { days?: number; subfield?: string; min_score?: number }) => {
      const q = new URLSearchParams();
      if (params?.days) q.set("days", String(params.days));
      if (params?.subfield) q.set("subfield", params.subfield);
      if (params?.min_score) q.set("min_score", String(params.min_score));
      return get<{ papers: Paper[]; count: number }>(`/api/papers/?${q}`);
    },
  },
  subfields: {
    list: () => get<Subfield[]>("/api/subfields/"),
    feed: (slug: string, days = 180) =>
      get<{ slug: string; name: string; papers: Paper[]; count: number }>(
        `/api/subfields/${slug}?days=${days}`
      ),
  },
  literature: {
    list: () => get<LitReview[]>("/api/literature/"),
    get: (subfield: string) => get<LitReview>(`/api/literature/${subfield}`),
  },
  openProblems: {
    clusters: (urgency?: string) =>
      get<{ clusters: OpenProblemCluster[]; count: number }>(
        `/api/open-problems/clusters${urgency ? `?urgency=${urgency}` : ""}`
      ),
  },
};
