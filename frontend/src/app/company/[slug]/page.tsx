"use client";

import { useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useStore } from "@/lib/store";
import { t } from "@/lib/i18n";
import { ScoreBadge } from "@/components/score-badge";
import { AuditCard } from "@/components/audit-card";
import { faviconUrl } from "@/lib/utils";

export default function CompanyPage() {
  const params = useParams();
  const slug = params.slug as string;
  const { currentCompany: company, companyAudits, companyAuditsHasMore, fetchCompany, fetchCompanyAudits } = useStore();

  useEffect(() => { if (slug) fetchCompany(slug); }, [slug]);

  if (!company) return <div className="max-w-3xl mx-auto px-4 py-16 text-center"><p className="text-accent animate-pulse">LOADING...</p></div>;

  const trendVal = company.trend_30d || 0;
  const trendColor = trendVal >= 0 ? "text-green" : "text-red";

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <Link href="/" className="text-xs text-muted hover:text-accent uppercase tracking-wider">← {t("back_to_feed")}</Link>

      <header className="py-6 mb-6">
        <div className="flex items-center gap-6">
          <div className="w-20 h-20 flex-shrink-0 flex items-center justify-center border-2 border-border bg-bg2">
            <img src={faviconUrl(company.domain, 64)} alt={company.name} width={48} height={48} className="w-12 h-12" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl md:text-3xl font-bold uppercase tracking-wider" data-testid="company-name">
              {company.name}
            </h1>
            <div className="flex items-center gap-3 mt-1 text-xs text-muted uppercase tracking-wider">
              <span>{company.domain}</span>
              <span className="btag">{company.category}</span>
            </div>
            <div className="flex items-center gap-4 mt-2">
              <span className={`font-bold ${trendColor}`}>
                {trendVal >= 0 ? "↑" : "↓"} {Math.abs(trendVal).toFixed(1)}
              </span>
              <span className="text-xs text-muted">{company.total_audits} AUDITS</span>
            </div>
          </div>
          <ScoreBadge score={company.trust_score} size="lg" />
        </div>
        <div className="h-[2px] bg-accent mt-4" />
      </header>

      {/* Top Findings */}
      {company.top_findings?.length > 0 && (
        <section className="mb-8 border-b border-border pb-6">
          <h2 className="text-xs text-accent uppercase tracking-widest font-bold mb-3">{t("top_findings")}</h2>
          <div className="flex flex-wrap gap-2">
            {company.top_findings.map((f) => (
              <span key={f} className="btag text-xs text-muted border border-border px-2 py-1">{f}</span>
            ))}
          </div>
        </section>
      )}

      {/* Audits */}
      <section className="mb-8">
        <h2 className="text-xs text-accent uppercase tracking-widest font-bold mb-3">
          {t("audits")} ({company.total_audits})
        </h2>
        {companyAudits.length === 0 ? (
          <p className="text-sm text-muted">// {t("no_audits")}</p>
        ) : (
          <div className="flex flex-col gap-3">
            {companyAudits.map((a) => <AuditCard key={a.id} audit={a} />)}
          </div>
        )}
        {companyAuditsHasMore && companyAudits.length > 0 && (
          <div className="text-center py-4">
            <button onClick={() => fetchCompanyAudits(slug)} className="filter-pill hover:filter-pill-active">{t("load_more")}</button>
          </div>
        )}
      </section>

      <footer className="text-center py-6 border-t border-border">
        <Link href="/" className="text-xs text-muted hover:text-accent uppercase tracking-wider">← {t("back_to_feed")}</Link>
      </footer>
    </div>
  );
}
