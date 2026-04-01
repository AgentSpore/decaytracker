export type Locale = "en" | "ru" | "cn";

const translations = {
  en: {
    // Masthead
    masthead: "THE TRUST FEED",
    tagline: "AI audits everything you buy",
    // URL input
    url_placeholder: "Paste any URL to audit...",
    audit_btn: "Audit",
    audit_queued: "Audit queued!",
    audit_done: "Audit complete!",
    audit_error: "Audit failed",
    // Filters
    filter_all: "All",
    filter_products: "Products",
    filter_apps: "Apps",
    filter_places: "Places",
    filter_companies: "Companies",
    filter_websites: "Websites",
    // Severity filters
    sev_all: "All",
    sev_critical: "Critical",
    sev_warning: "Warning",
    sev_info: "Info",
    sev_positive: "Positive",
    sev_clean: "Clean",
    // Audit card
    trust_score: "Trust Score",
    findings: "findings",
    finding: "finding",
    share: "Share",
    link_copied: "Link copied!",
    views: "views",
    // Audit detail
    ai_summary: "AI Summary",
    evidence: "Evidence",
    confidence: "Confidence",
    original_url: "Original URL",
    metadata: "Metadata",
    back_to_feed: "Back to Feed",
    // Company
    company: "Company",
    top_findings: "Top Findings",
    audits: "Audits",
    trend: "Trend",
    total_audits: "Total Audits",
    // Leaderboard
    leaderboard: "Leaderboard",
    most_trusted: "Most Trusted",
    least_trusted: "Least Trusted",
    rank: "Rank",
    // Finding types
    type_pricing: "Pricing",
    type_privacy: "Privacy",
    type_quality: "Quality",
    type_support: "Support",
    type_security: "Security",
    type_ads: "Ads",
    type_dark_pattern: "Dark Pattern",
    type_sustainability: "Sustainability",
    type_accessibility: "Accessibility",
    type_transparency: "Transparency",
    type_other: "Other",
    // Time
    just_now: "just now",
    min_ago: "m ago",
    hour_ago: "h ago",
    day_ago: "d ago",
    // Common
    loading: "Loading...",
    load_more: "Load more",
    no_results: "No results found",
    no_audits: "No audits yet",
    footer: "The Trust Feed \u00b7 DecayTracker v2.0.0 \u00b7 AI-powered audits",
    // Nav
    nav_feed: "Feed",
    nav_top: "Top",
  },
  ru: {
    masthead: "\u041b\u0415\u041d\u0422\u0410 \u0414\u041e\u0412\u0415\u0420\u0418\u042f",
    tagline: "\u0418\u0418 \u043f\u0440\u043e\u0432\u0435\u0440\u044f\u0435\u0442 \u0432\u0441\u0451 \u0447\u0442\u043e \u0432\u044b \u043f\u043e\u043a\u0443\u043f\u0430\u0435\u0442\u0435",
    url_placeholder: "\u0412\u0441\u0442\u0430\u0432\u044c\u0442\u0435 URL \u0434\u043b\u044f \u0430\u0443\u0434\u0438\u0442\u0430...",
    audit_btn: "\u0410\u0443\u0434\u0438\u0442",
    audit_queued: "\u0410\u0443\u0434\u0438\u0442 \u0432 \u043e\u0447\u0435\u0440\u0435\u0434\u0438!",
    audit_done: "\u0410\u0443\u0434\u0438\u0442 \u0437\u0430\u0432\u0435\u0440\u0448\u0451\u043d!",
    audit_error: "\u041e\u0448\u0438\u0431\u043a\u0430 \u0430\u0443\u0434\u0438\u0442\u0430",
    filter_all: "\u0412\u0441\u0435",
    filter_products: "\u0422\u043e\u0432\u0430\u0440\u044b",
    filter_apps: "\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f",
    filter_places: "\u041c\u0435\u0441\u0442\u0430",
    filter_companies: "\u041a\u043e\u043c\u043f\u0430\u043d\u0438\u0438",
    filter_websites: "\u0421\u0430\u0439\u0442\u044b",
    sev_all: "\u0412\u0441\u0435",
    sev_critical: "\u041a\u0440\u0438\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0439",
    sev_warning: "\u041f\u0440\u0435\u0434\u0443\u043f\u0440\u0435\u0436\u0434\u0435\u043d\u0438\u0435",
    sev_info: "\u0418\u043d\u0444\u043e",
    sev_positive: "\u041f\u043e\u043b\u043e\u0436\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0439",
    sev_clean: "\u0427\u0438\u0441\u0442\u044b\u0439",
    trust_score: "\u0418\u043d\u0434\u0435\u043a\u0441 \u0434\u043e\u0432\u0435\u0440\u0438\u044f",
    findings: "\u043d\u0430\u0445\u043e\u0434\u043a\u0438",
    finding: "\u043d\u0430\u0445\u043e\u0434\u043a\u0430",
    share: "\u041f\u043e\u0434\u0435\u043b\u0438\u0442\u044c\u0441\u044f",
    link_copied: "\u0421\u0441\u044b\u043b\u043a\u0430 \u0441\u043a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u043d\u0430!",
    views: "\u043f\u0440\u043e\u0441\u043c\u043e\u0442\u0440\u044b",
    ai_summary: "\u0410\u043d\u0430\u043b\u0438\u0437 \u0418\u0418",
    evidence: "\u0414\u043e\u043a\u0430\u0437\u0430\u0442\u0435\u043b\u044c\u0441\u0442\u0432\u043e",
    confidence: "\u0423\u0432\u0435\u0440\u0435\u043d\u043d\u043e\u0441\u0442\u044c",
    original_url: "\u0418\u0441\u0445\u043e\u0434\u043d\u044b\u0439 URL",
    metadata: "\u041c\u0435\u0442\u0430\u0434\u0430\u043d\u043d\u044b\u0435",
    back_to_feed: "\u041d\u0430\u0437\u0430\u0434 \u043a \u043b\u0435\u043d\u0442\u0435",
    company: "\u041a\u043e\u043c\u043f\u0430\u043d\u0438\u044f",
    top_findings: "\u0413\u043b\u0430\u0432\u043d\u044b\u0435 \u043d\u0430\u0445\u043e\u0434\u043a\u0438",
    audits: "\u0410\u0443\u0434\u0438\u0442\u044b",
    trend: "\u0422\u0440\u0435\u043d\u0434",
    total_audits: "\u0412\u0441\u0435\u0433\u043e \u0430\u0443\u0434\u0438\u0442\u043e\u0432",
    leaderboard: "\u0420\u0435\u0439\u0442\u0438\u043d\u0433",
    most_trusted: "\u0421\u0430\u043c\u044b\u0435 \u043d\u0430\u0434\u0451\u0436\u043d\u044b\u0435",
    least_trusted: "\u0421\u0430\u043c\u044b\u0435 \u043d\u0435\u043d\u0430\u0434\u0451\u0436\u043d\u044b\u0435",
    rank: "\u041c\u0435\u0441\u0442\u043e",
    type_pricing: "\u0426\u0435\u043d\u044b",
    type_privacy: "\u041f\u0440\u0438\u0432\u0430\u0442\u043d\u043e\u0441\u0442\u044c",
    type_quality: "\u041a\u0430\u0447\u0435\u0441\u0442\u0432\u043e",
    type_support: "\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430",
    type_security: "\u0411\u0435\u0437\u043e\u043f\u0430\u0441\u043d\u043e\u0441\u0442\u044c",
    type_ads: "\u0420\u0435\u043a\u043b\u0430\u043c\u0430",
    type_dark_pattern: "\u0422\u0451\u043c\u043d\u044b\u0439 \u043f\u0430\u0442\u0442\u0435\u0440\u043d",
    type_sustainability: "\u0423\u0441\u0442\u043e\u0439\u0447\u0438\u0432\u043e\u0441\u0442\u044c",
    type_accessibility: "\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u043e\u0441\u0442\u044c",
    type_transparency: "\u041f\u0440\u043e\u0437\u0440\u0430\u0447\u043d\u043e\u0441\u0442\u044c",
    type_other: "\u0414\u0440\u0443\u0433\u043e\u0435",
    just_now: "\u0442\u043e\u043b\u044c\u043a\u043e \u0447\u0442\u043e",
    min_ago: "\u043c \u043d\u0430\u0437\u0430\u0434",
    hour_ago: "\u0447 \u043d\u0430\u0437\u0430\u0434",
    day_ago: "\u0434 \u043d\u0430\u0437\u0430\u0434",
    loading: "\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430...",
    load_more: "\u0417\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044c \u0435\u0449\u0451",
    no_results: "\u041d\u0438\u0447\u0435\u0433\u043e \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043e",
    no_audits: "\u0410\u0443\u0434\u0438\u0442\u043e\u0432 \u043f\u043e\u043a\u0430 \u043d\u0435\u0442",
    footer: "\u041b\u0435\u043d\u0442\u0430 \u0414\u043e\u0432\u0435\u0440\u0438\u044f \u00b7 DecayTracker v2.0.0 \u00b7 \u0410\u0443\u0434\u0438\u0442\u044b \u043d\u0430 \u0418\u0418",
    nav_feed: "\u041b\u0435\u043d\u0442\u0430",
    nav_top: "\u0422\u043e\u043f",
  },
  cn: {
    masthead: "\u4fe1\u4efb\u52a8\u6001",
    tagline: "AI\u5ba1\u6838\u60a8\u8d2d\u4e70\u7684\u4e00\u5207",
    url_placeholder: "\u7c98\u8d34\u4efb\u4f55URL\u8fdb\u884c\u5ba1\u6838...",
    audit_btn: "\u5ba1\u6838",
    audit_queued: "\u5ba1\u6838\u5df2\u6392\u961f!",
    audit_done: "\u5ba1\u6838\u5b8c\u6210!",
    audit_error: "\u5ba1\u6838\u5931\u8d25",
    filter_all: "\u5168\u90e8",
    filter_products: "\u4ea7\u54c1",
    filter_apps: "\u5e94\u7528",
    filter_places: "\u5730\u70b9",
    filter_companies: "\u516c\u53f8",
    filter_websites: "\u7f51\u7ad9",
    sev_all: "\u5168\u90e8",
    sev_critical: "\u4e25\u91cd",
    sev_warning: "\u8b66\u544a",
    sev_info: "\u4fe1\u606f",
    sev_positive: "\u79ef\u6781",
    sev_clean: "\u6e05\u6d01",
    trust_score: "\u4fe1\u4efb\u5206\u6570",
    findings: "\u53d1\u73b0",
    finding: "\u53d1\u73b0",
    share: "\u5206\u4eab",
    link_copied: "\u94fe\u63a5\u5df2\u590d\u5236!",
    views: "\u6d4f\u89c8",
    ai_summary: "AI\u5206\u6790",
    evidence: "\u8bc1\u636e",
    confidence: "\u7f6e\u4fe1\u5ea6",
    original_url: "\u539f\u59cbURL",
    metadata: "\u5143\u6570\u636e",
    back_to_feed: "\u8fd4\u56de\u52a8\u6001",
    company: "\u516c\u53f8",
    top_findings: "\u4e3b\u8981\u53d1\u73b0",
    audits: "\u5ba1\u6838",
    trend: "\u8d8b\u52bf",
    total_audits: "\u5ba1\u6838\u603b\u6570",
    leaderboard: "\u6392\u884c\u699c",
    most_trusted: "\u6700\u53d7\u4fe1\u4efb",
    least_trusted: "\u6700\u4e0d\u53ef\u4fe1",
    rank: "\u6392\u540d",
    type_pricing: "\u5b9a\u4ef7",
    type_privacy: "\u9690\u79c1",
    type_quality: "\u8d28\u91cf",
    type_support: "\u652f\u6301",
    type_security: "\u5b89\u5168",
    type_ads: "\u5e7f\u544a",
    type_dark_pattern: "\u6697\u6a21\u5f0f",
    type_sustainability: "\u53ef\u6301\u7eed\u6027",
    type_accessibility: "\u65e0\u969c\u788d",
    type_transparency: "\u900f\u660e\u5ea6",
    type_other: "\u5176\u4ed6",
    just_now: "\u521a\u521a",
    min_ago: "\u5206\u524d",
    hour_ago: "\u5c0f\u65f6\u524d",
    day_ago: "\u5929\u524d",
    loading: "\u52a0\u8f7d\u4e2d...",
    load_more: "\u52a0\u8f7d\u66f4\u591a",
    no_results: "\u672a\u627e\u5230\u7ed3\u679c",
    no_audits: "\u6682\u65e0\u5ba1\u6838",
    footer: "\u4fe1\u4efb\u52a8\u6001 \u00b7 DecayTracker v2.0.0 \u00b7 AI\u9a71\u52a8\u5ba1\u6838",
    nav_feed: "\u52a8\u6001",
    nav_top: "\u6392\u884c",
  },
} as const;

type TranslationKey = keyof typeof translations.en;

let currentLocale: Locale = "en";

export function getLocale(): Locale {
  if (typeof window !== "undefined") {
    const saved = localStorage.getItem("dt_locale") as Locale | null;
    if (saved && saved in translations) {
      currentLocale = saved;
      return saved;
    }
  }
  return currentLocale;
}

export function setLocale(locale: Locale) {
  currentLocale = locale;
  if (typeof window !== "undefined") {
    localStorage.setItem("dt_locale", locale);
  }
}

export function t(key: TranslationKey): string {
  return translations[currentLocale]?.[key] || translations.en[key] || key;
}

export const localeLabels: Record<Locale, string> = {
  en: "EN",
  ru: "RU",
  cn: "CN",
};
