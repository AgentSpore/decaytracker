"use client";

function scoreClass(score: number): string {
  if (score <= 30) return "score-red";
  if (score <= 60) return "score-amber";
  if (score <= 80) return "score-green";
  return "score-bright";
}

export function ScoreBadge({ score, size = "md" }: { score: number; size?: "sm" | "md" | "lg" }) {
  const sizes = { sm: "text-2xl", md: "text-4xl", lg: "text-6xl" };
  return (
    <div className="text-right flex-shrink-0">
      <span className={`${sizes[size]} font-mono font-bold ${scoreClass(score)}`}>
        {Math.round(score)}
      </span>
      <div className="text-[10px] uppercase tracking-widest text-muted">trust</div>
    </div>
  );
}
