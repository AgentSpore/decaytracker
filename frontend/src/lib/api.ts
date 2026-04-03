const BASE = process.env.NEXT_PUBLIC_API_URL ?? (typeof window !== "undefined" && window.location.hostname !== "localhost" ? "" : "http://localhost:8790");

/* ── Types (match backend response exactly) ── */

export interface AuditFinding {
  id: number;
  type: string;
  severity: string;
  title: string;
  description: string;
  evidence_url: string;
  confidence: number;
}

export interface AuditCard {
  id: number;
  company_id: number;
  company_name: string;
  company_slug: string;
  company_logo: string;
  url: string;
  platform: string;
  title: string;
  subtitle: string;
  trust_score: number;
  severity: string;
  ai_summary: string;
  findings_count: number;
  status: string;
  views: number;
  created_at: string;
}

export interface AuditDetail extends AuditCard {
  findings: AuditFinding[];
  metadata: Record<string, unknown>;
  queue_position: number;
  queue_total: number;
}

export interface Company {
  id: number;
  name: string;
  slug: string;
  domain: string;
  category: string;
  description: string;
  logo_url: string;
  trust_score: number;
  total_audits: number;
  trend_30d: number;
  top_findings: string[];
}

export interface CompanyDetail extends Company {
  recent_audits: AuditCard[];
}

export interface FeedResponse {
  items: AuditCard[];
  total: number;
  page: number;
  per_page: number;
  has_more: boolean;
}

/* ── Helpers ── */

async function apiFetch<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...opts,
    headers: { "Content-Type": "application/json", ...opts?.headers },
  });
  if (!res.ok) {
    // Try to extract human-readable detail from FastAPI error response
    try {
      const body = await res.json();
      const detail = body?.detail;
      if (typeof detail === "string") throw new Error(detail);
    } catch (e) {
      if (e instanceof Error && e.message !== "Unexpected end of JSON input") throw e;
    }
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

/* ── API ── */

export const api = {
  submitAudit: (url: string) =>
    apiFetch<{ audit_id: number; company_id: number; company_slug: string; platform: string; status: string }>("/api/audit", {
      method: "POST",
      body: JSON.stringify({ url }),
    }),

  getAudit: (id: number) => apiFetch<AuditDetail>(`/api/audit/${id}`),

  getFeed: (page = 1, perPage = 20, platform?: string, severity?: string) => {
    const params = new URLSearchParams({
      page: String(page),
      per_page: String(perPage),
    });
    if (platform) params.set("platform", platform);
    if (severity) params.set("severity", severity);
    return apiFetch<FeedResponse>(`/api/feed?${params}`);
  },

  getCompanies: (order = "worst", limit = 20) =>
    apiFetch<Company[]>(`/api/companies?order=${order}&limit=${limit}`),

  getCompany: (slug: string) => apiFetch<CompanyDetail>(`/api/company/${slug}`),

  getCompanyAudits: (slug: string, page = 1) =>
    apiFetch<FeedResponse>(`/api/company/${slug}/audits?page=${page}`),

  retryAudit: (id: number) =>
    apiFetch<{ audit_id: number; status: string }>(`/api/audit/${id}/retry`, { method: "POST" }),
};
