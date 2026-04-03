"use client";

import { useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useStore } from "@/lib/store";
import { t } from "@/lib/i18n";
import { ScoreBadge } from "@/components/score-badge";
import { FindingCard } from "@/components/finding-card";
import { PlatformTag } from "@/components/platform-tag";
import { timeAgo, severityClass, loc } from "@/lib/utils";

export default function AuditDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const { currentAudit: audit, fetchAudit } = useStore();

  useEffect(() => { if (id) fetchAudit(id); }, [id]);

  // Auto-refresh while pending/processing
  useEffect(() => {
    if (!audit || (audit.status !== "pending" && audit.status !== "processing")) return;
    const interval = setInterval(() => fetchAudit(id), 5000);
    return () => clearInterval(interval);
  }, [audit?.status, id, fetchAudit]);

  if (!audit) return <div className="max-w-3xl mx-auto px-4 py-16 text-center"><p className="text-accent animate-pulse">LOADING...</p></div>;

  // Show status page for pending/processing
  if (audit.status === "pending" || audit.status === "processing") {
    const queuePos = (audit as Record<string, unknown>).queue_position as number || 0;
    const queueTotal = (audit as Record<string, unknown>).queue_total as number || 0;
    const isPending = audit.status === "pending";
    const etaMin = isPending ? queuePos * 1.5 : 1;

    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <Link href="/feed" className="text-xs text-muted hover:text-accent uppercase tracking-wider">← {t("back_to_feed")}</Link>
        <div className="mt-12">
          <p className="text-accent font-mono text-sm mb-2">[{audit.status.toUpperCase()}]</p>
          <h1 className="text-xl font-bold mb-4">{loc(audit.title) || audit.url}</h1>

          {isPending ? (
            <>
              <p className="text-accent font-mono mb-2">{t("queued")}<span className="terminal-cursor" /></p>
              {queueTotal > 0 && (
                <p className="text-xs text-muted font-mono mb-4">
                  // POSITION {queuePos} OF {queueTotal} IN QUEUE
                </p>
              )}
            </>
          ) : (
            <>
              <p className="text-accent animate-pulse font-mono mb-2">{t("scanning")}...</p>
              <div className="mt-2 h-1 bg-border overflow-hidden max-w-xs mx-auto"><div className="indeterminate-bar" /></div>
            </>
          )}

          <div className="mt-6 border border-border p-4 text-left max-w-md mx-auto">
            <p className="text-xs text-accent font-mono font-bold mb-2">// AUDIT STAGES:</p>
            <p className={`text-xs font-mono mb-1 ${!isPending ? "text-accent" : "text-muted"}`}>
              {!isPending ? "►" : "○"} 1. SCRAPING PAGE...
            </p>
            <p className="text-xs font-mono text-muted mb-1">○ 2. GOOGLE SEARCH: SCAMS & FRAUD</p>
            <p className="text-xs font-mono text-muted mb-1">○ 3. GOOGLE SEARCH: FAKE REVIEWS</p>
            <p className="text-xs font-mono text-muted mb-1">○ 4. GOOGLE SEARCH: DARK PATTERNS</p>
            <p className="text-xs font-mono text-muted mb-1">○ 5. GOOGLE SEARCH: TRUSTPILOT</p>
            <p className="text-xs font-mono text-muted mb-1">○ 6. AI ANALYSIS</p>
          </div>

          <p className="text-xs text-muted mt-4 font-mono">
            // ESTIMATED TIME: ~{Math.ceil(etaMin)} MIN
          </p>
          <p className="text-[10px] text-muted/50 mt-2 font-mono">AUTO-REFRESHING EVERY 5S</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      <Link href="/feed" className="text-xs text-muted hover:text-accent uppercase tracking-wider" data-testid="back-link">
        ← {t("back_to_feed")}
      </Link>

      {/* Header */}
      <header className="py-6 mb-6">
        <div className="flex items-start gap-5">
          <div className="w-16 h-16 flex-shrink-0 flex items-center justify-center border-2 border-border bg-bg2">
            {audit.company_logo ? (
              <img src={audit.company_logo} alt="" width={40} height={40} className="w-10 h-10" />
            ) : (
              <span className="text-2xl font-bold text-accent">{audit.title?.[0]}</span>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-2">
              <PlatformTag platform={audit.platform} />
              <span className={`btag text-xs font-bold uppercase tracking-wider ${severityClass(audit.severity)}`}>
                {audit.severity}
              </span>
            </div>
            <h1 className="text-xl md:text-2xl font-bold leading-tight" data-testid="audit-title">
              {loc(audit.title)}
            </h1>
            <div className="flex items-center gap-3 mt-2 text-xs text-muted uppercase tracking-wider">
              <span>{timeAgo(audit.created_at)}</span>
              <span>{audit.views} views</span>
              {audit.company_slug && (
                <Link href={`/company/${audit.company_slug}`} className="text-accent hover:underline">
                  [{audit.company_name}] →
                </Link>
              )}
            </div>
          </div>
          <ScoreBadge score={audit.trust_score} size="lg" />
        </div>
        <div className="h-[2px] bg-accent mt-4" />
      </header>

      {/* AI Summary */}
      {audit.ai_summary && (
        <section className="mb-8 border-b border-border pb-6">
          <h2 className="text-xs text-accent uppercase tracking-widest font-bold mb-3">{t("ai_summary")}</h2>
          <p className="text-sm leading-relaxed text-muted">{loc(audit.ai_summary)}</p>
        </section>
      )}

      {/* Findings */}
      <section className="mb-8">
        <h2 className="text-xs text-accent uppercase tracking-widest font-bold mb-3">
          {t("findings")} ({audit.findings?.length || 0})
        </h2>
        <div className="flex flex-col gap-2" data-testid="findings-list">
          {audit.findings?.length === 0 ? (
            <p className="text-sm text-muted">// {t("no_results")}</p>
          ) : (
            audit.findings?.map((f) => <FindingCard key={f.id} finding={f} />)
          )}
        </div>
      </section>

      {/* URL */}
      <section className="mb-8 border-b border-border pb-6">
        <h2 className="text-xs text-accent uppercase tracking-widest font-bold mb-3">{t("original_url")}</h2>
        <a href={audit.url} target="_blank" rel="noopener noreferrer" className="text-sm text-accent hover:underline break-all">
          {audit.url}
        </a>
      </section>

      <footer className="text-center py-6 border-t border-border">
        <Link href="/feed" className="text-xs text-muted hover:text-accent uppercase tracking-wider">← {t("back_to_feed")}</Link>
      </footer>
    </div>
  );
}
