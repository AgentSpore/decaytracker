"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useStore } from "@/lib/store";
import { t } from "@/lib/i18n";
import { faviconUrl, scoreColorClass } from "@/lib/utils";
import type { Company } from "@/lib/api";

function Row({ company, rank }: { company: Company; rank: number }) {
  const trendVal = company.trend_30d || 0;
  const trendColor = trendVal >= 0 ? "text-green" : "text-red";

  return (
    <Link href={`/company/${company.slug}`} className="flex items-center gap-3 p-3 border border-border bg-card hover:bg-card-hover hover:border-accent/30 transition-all">
      <span className="text-lg font-bold text-muted w-8 text-center">{rank}</span>
      <div className="w-8 h-8 flex-shrink-0 flex items-center justify-center bg-bg2 border border-border">
        <img src={faviconUrl(company.domain)} alt="" width={20} height={20} className="w-5 h-5" />
      </div>
      <span className="flex-1 min-w-0 font-bold text-sm truncate uppercase">{company.name}</span>
      <span className={`text-xl font-bold w-12 text-right ${scoreColorClass(company.trust_score)}`}>
        {Math.round(company.trust_score)}
      </span>
      <span className="text-xs text-muted w-10 text-center">{company.total_audits}</span>
      <span className={`text-xs ${trendColor} w-12 text-right`}>
        {trendVal >= 0 ? "↑" : "↓"} {Math.abs(trendVal).toFixed(1)}
      </span>
    </Link>
  );
}

export default function LeaderboardPage() {
  const { leaderboard, fetchLeaderboard } = useStore();
  useEffect(() => { fetchLeaderboard(); }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <Link href="/feed" className="text-xs text-muted hover:text-accent uppercase tracking-wider">← {t("back_to_feed")}</Link>

      <header className="py-6 mb-8">
        <h1 className="text-2xl font-bold text-accent uppercase tracking-wider">{t("leaderboard")}</h1>
        <div className="h-[2px] bg-accent mt-2" />
      </header>

      <div className="grid md:grid-cols-2 gap-8">
        <section>
          <h2 className="text-sm font-bold text-green uppercase tracking-widest mb-4">{t("most_trusted")}</h2>
          <div className="flex items-center gap-3 px-3 py-2 text-[10px] text-muted uppercase tracking-widest border-b border-border mb-2">
            <span className="w-8 text-center">#</span><span className="w-8" /><span className="flex-1">Company</span>
            <span className="w-12 text-right">Score</span><span className="w-10 text-center">Audits</span><span className="w-12 text-right">Trend</span>
          </div>
          <div className="flex flex-col gap-1">
            {leaderboard.best.map((c, i) => <Row key={c.slug} company={c} rank={i + 1} />)}
          </div>
        </section>

        <section>
          <h2 className="text-sm font-bold text-red uppercase tracking-widest mb-4">{t("least_trusted")}</h2>
          <div className="flex items-center gap-3 px-3 py-2 text-[10px] text-muted uppercase tracking-widest border-b border-border mb-2">
            <span className="w-8 text-center">#</span><span className="w-8" /><span className="flex-1">Company</span>
            <span className="w-12 text-right">Score</span><span className="w-10 text-center">Audits</span><span className="w-12 text-right">Trend</span>
          </div>
          <div className="flex flex-col gap-1">
            {leaderboard.worst.map((c, i) => <Row key={c.slug} company={c} rank={i + 1} />)}
          </div>
        </section>
      </div>

      <footer className="text-center py-8 mt-8 border-t border-border">
        <p className="text-[10px] text-muted uppercase tracking-widest">{t("footer")}</p>
      </footer>
    </div>
  );
}
