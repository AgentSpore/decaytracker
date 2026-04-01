import { t, getLocale } from "./i18n";

export function timeAgo(dateStr: string): string {
  const now = Date.now();
  const date = new Date(dateStr + "Z").getTime();
  const diffSec = Math.floor((now - date) / 1000);
  if (diffSec < 60) return t("just_now");
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}${t("min_ago")}`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}${t("hour_ago")}`;
  return `${Math.floor(diffSec / 86400)}${t("day_ago")}`;
}

export function faviconUrl(domain: string, size = 32): string {
  return `https://www.google.com/s2/favicons?domain=${domain}&sz=${size}`;
}

export function scoreColorClass(score: number): string {
  if (score <= 30) return "score-red";
  if (score <= 60) return "score-amber";
  if (score <= 80) return "score-green";
  return "score-bright";
}

export function severityClass(severity: string): string {
  const map: Record<string, string> = {
    critical: "text-red", warning: "text-amber",
    info: "text-muted", positive: "text-green", clean: "text-green",
  };
  return map[severity] || "text-muted";
}

/**
 * Resolve a localized field. The value can be:
 * - A plain string (old audits) → returned as-is
 * - A JSON string like '{"en":"...","ru":"...","cn":"..."}' → parsed and locale picked
 * - An object {en, ru, cn} → locale picked directly
 */
export function loc(value: unknown): string {
  if (!value) return "";
  if (typeof value === "object" && value !== null) {
    const obj = value as Record<string, string>;
    const locale = getLocale();
    return obj[locale] || obj["en"] || Object.values(obj)[0] || "";
  }
  if (typeof value === "string") {
    // Try parsing as JSON
    if (value.startsWith("{")) {
      try {
        const obj = JSON.parse(value) as Record<string, string>;
        const locale = getLocale();
        return obj[locale] || obj["en"] || value;
      } catch {
        return value;
      }
    }
    return value;
  }
  return String(value);
}
