"use client";

import type { AuditFinding } from "@/lib/api";
import { t } from "@/lib/i18n";
import { loc } from "@/lib/utils";

const sevIcon: Record<string, string> = {
  critical: "!!", warning: "!~", info: "--", positive: "++",
};

const sevColor: Record<string, string> = {
  critical: "text-red border-red", warning: "text-amber border-amber",
  info: "text-muted border-border", positive: "text-green border-green",
};

export function FindingCard({ finding }: { finding: AuditFinding }) {
  const color = sevColor[finding.severity] || sevColor.info;
  const icon = sevIcon[finding.severity] || "--";
  const confidence = Math.round(finding.confidence * 100);

  return (
    <div className={`border border-border p-4 border-l-3 ${color.split(" ").pop()}`} data-testid="finding-card">
      <div className="flex items-center gap-3 mb-2">
        <span className={`font-bold text-sm ${color.split(" ")[0]}`}>{icon}</span>
        <span className="btag text-xs text-muted uppercase tracking-wider">{finding.type}</span>
      </div>

      <h4 className="font-bold text-sm mb-1">{loc(finding.title)}</h4>
      {finding.description && (
        <p className="text-sm text-muted leading-relaxed mb-2">{loc(finding.description)}</p>
      )}

      {finding.evidence_url && (
        <a
          href={finding.evidence_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block text-xs text-accent hover:underline mb-2"
        >
          [{t("evidence")}] →
        </a>
      )}

      <div className="flex items-center gap-2 mt-2">
        <span className="text-[10px] text-muted uppercase tracking-wider">{t("confidence")}</span>
        <div className="flex-1 h-1 bg-border">
          <div className="h-full bg-accent transition-all" style={{ width: `${confidence}%` }} />
        </div>
        <span className="text-xs text-muted">{confidence}%</span>
      </div>
    </div>
  );
}
