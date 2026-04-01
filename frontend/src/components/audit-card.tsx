"use client";

import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";
import type { AuditCard as AuditCardType } from "@/lib/api";
import { api } from "@/lib/api";
import { ScoreBadge } from "./score-badge";
import { t } from "@/lib/i18n";
import { timeAgo, loc } from "@/lib/utils";

function PendingCard({ audit }: { audit: AuditCardType }) {
  return (
    <article
      className="bg-card border border-border p-5 card-pulse"
      data-testid="audit-card-pending"
    >
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 flex-shrink-0 flex items-center justify-center border border-border bg-bg2 mt-0.5">
          {audit.company_logo ? (
            <img src={audit.company_logo} alt="" width={28} height={28} className="w-7 h-7 opacity-50" />
          ) : (
            <span className="text-sm font-bold text-accent/40">{audit.title?.[0] || "?"}</span>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-muted uppercase tracking-wider">{audit.company_name}</span>
            <span className="text-xs text-muted">&middot;</span>
            <span className="text-xs text-muted">{timeAgo(audit.created_at)}</span>
          </div>
          <div className="text-xs font-bold uppercase tracking-wider mb-2 text-accent/40">
            <span className="btag">PENDING</span>
          </div>
          <p className="font-mono text-sm text-muted mb-1 truncate">{audit.url}</p>
          <p className="font-mono text-sm text-accent/50">
            {t("queued")}<span className="terminal-cursor" />
          </p>
        </div>
      </div>
    </article>
  );
}

function ProcessingCard({ audit }: { audit: AuditCardType }) {
  return (
    <article
      className="bg-card border border-accent/50 p-5 glow-border"
      data-testid="audit-card-processing"
    >
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 flex-shrink-0 flex items-center justify-center border border-accent/30 bg-bg2 mt-0.5">
          {audit.company_logo ? (
            <img src={audit.company_logo} alt="" width={28} height={28} className="w-7 h-7" />
          ) : (
            <span className="text-sm font-bold text-accent">{audit.title?.[0] || "?"}</span>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-muted uppercase tracking-wider">{audit.company_name}</span>
            <span className="text-xs text-muted">&middot;</span>
            <span className="text-xs text-muted">{timeAgo(audit.created_at)}</span>
          </div>
          <div className="text-xs font-bold uppercase tracking-wider mb-2 text-accent">
            <span className="btag">PROCESSING</span>
          </div>
          <p className="font-mono text-sm text-muted mb-1 truncate">{audit.url}</p>
          <p className="font-mono text-sm text-accent">
            {t("scanning")}<span className="scanning-dots" />
          </p>
          {/* Indeterminate progress bar */}
          <div className="mt-3 h-1 bg-border overflow-hidden">
            <div className="indeterminate-bar" />
          </div>
        </div>
      </div>
    </article>
  );
}

function FailedCard({ audit }: { audit: AuditCardType }) {
  const [retrying, setRetrying] = useState(false);

  const handleRetry = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (retrying) return;
    setRetrying(true);
    try {
      await api.retryAudit(audit.id);
      toast.success(t("audit_queued"));
    } catch {
      toast.error(t("audit_error"));
    } finally {
      setRetrying(false);
    }
  };

  return (
    <article
      className="bg-card border border-border border-l-3 border-l-red p-5"
      data-testid="audit-card-failed"
    >
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 flex-shrink-0 flex items-center justify-center border border-red/30 bg-bg2 mt-0.5">
          {audit.company_logo ? (
            <img src={audit.company_logo} alt="" width={28} height={28} className="w-7 h-7 opacity-50" />
          ) : (
            <span className="text-sm font-bold text-red">{audit.title?.[0] || "?"}</span>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-muted uppercase tracking-wider">{audit.company_name}</span>
            <span className="text-xs text-muted">&middot;</span>
            <span className="text-xs text-muted">{timeAgo(audit.created_at)}</span>
          </div>
          <p className="font-mono text-sm text-red font-bold uppercase mb-3">
            {t("audit_failed_label")}
          </p>
          {audit.title && (
            <h3 className="font-bold text-[15px] leading-tight mb-3 text-muted">
              {loc(audit.title)}
            </h3>
          )}
          <button
            onClick={handleRetry}
            disabled={retrying}
            className="border border-red px-4 py-1.5 text-xs font-mono font-bold uppercase tracking-wider text-red hover:bg-red hover:text-bg transition-colors disabled:opacity-50"
            data-testid="retry-audit-btn"
          >
            {retrying ? "..." : t("retry")}
          </button>
        </div>
      </div>
    </article>
  );
}

function DoneCard({ audit }: { audit: AuditCardType }) {
  const handleShare = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    navigator.clipboard.writeText(`${window.location.origin}/audit/${audit.id}`).then(() => {
      toast.success(t("link_copied"));
    });
  };

  const sevClass = `card-sev-${audit.severity}`;
  const sevColor: Record<string, string> = {
    critical: "text-red", warning: "text-amber", clean: "text-green",
    positive: "text-green", info: "text-muted", neutral: "text-muted",
  };

  return (
    <Link href={`/audit/${audit.id}`} data-testid="audit-card">
      <article className={`bg-card border border-border ${sevClass} p-5 hover:bg-card-hover hover:border-accent/30 transition-all`}>
        <div className="flex items-start gap-4">
          {/* Logo */}
          <div className="w-10 h-10 flex-shrink-0 flex items-center justify-center border border-border bg-bg2 mt-0.5">
            {audit.company_logo ? (
              <img src={audit.company_logo} alt="" width={28} height={28} className="w-7 h-7" />
            ) : (
              <span className="text-sm font-bold text-accent">{audit.title?.[0] || "?"}</span>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs text-muted uppercase tracking-wider">{audit.company_name}</span>
              <span className="text-xs text-muted">&middot;</span>
              <span className="text-xs text-muted">{timeAgo(audit.created_at)}</span>
            </div>

            {/* Severity */}
            <div className={`text-xs font-bold uppercase tracking-wider mb-2 ${sevColor[audit.severity] || "text-muted"}`}>
              <span className="btag">{audit.severity}</span>
            </div>

            {/* Title + Score: stacked on mobile */}
            <div className="flex flex-col sm:flex-row sm:items-start sm:gap-4">
              <div className="flex-1 min-w-0">
                <h3 className="font-bold text-[15px] leading-tight mb-2 text-text">
                  {loc(audit.title)}
                </h3>

                {/* Summary */}
                {audit.ai_summary && (
                  <p className="text-sm text-muted leading-relaxed mb-3 line-clamp-2">
                    {loc(audit.ai_summary)}
                  </p>
                )}
              </div>

              {/* Score badge: hidden on mobile here, shown below */}
              <div className="hidden sm:block">
                <ScoreBadge score={audit.trust_score} size="sm" />
              </div>
            </div>

            {/* Score badge on mobile: below title */}
            <div className="sm:hidden mb-3">
              <ScoreBadge score={audit.trust_score} size="sm" />
            </div>

            {/* Meta */}
            <div className="flex items-center gap-4 text-xs text-muted uppercase tracking-wider">
              <span>{audit.views.toLocaleString()} {t("views")}</span>
              <span>{audit.findings_count} {t("findings")}</span>
              <button
                onClick={handleShare}
                className="ml-auto border border-border px-3 py-1 hover:border-accent hover:text-accent transition-colors uppercase"
                data-testid="share-btn"
              >
                {t("share")}
              </button>
            </div>
          </div>
        </div>
      </article>
    </Link>
  );
}

export function AuditCard({ audit }: { audit: AuditCardType }) {
  switch (audit.status) {
    case "pending":
      return <PendingCard audit={audit} />;
    case "processing":
      return <ProcessingCard audit={audit} />;
    case "failed":
      return <FailedCard audit={audit} />;
    default:
      return <DoneCard audit={audit} />;
  }
}
