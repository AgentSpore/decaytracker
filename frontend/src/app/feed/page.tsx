"use client";

import { useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { useStore } from "@/lib/store";
import { t, localeLabels, type Locale } from "@/lib/i18n";
import { AuditCard } from "@/components/audit-card";
import { UrlInput, type UrlInputHandle } from "@/components/url-input";

const FILTERS = [
  { key: "", label: "filter_all" },
  { key: "amazon_product", label: "filter_products" },
  { key: "appstore_app", label: "filter_apps" },
  { key: "gmaps_place", label: "filter_places" },
  { key: "website", label: "filter_websites" },
] as const;

const SUGGESTED_URLS = [
  "https://amazon.com",
  "https://netflix.com",
  "https://adobe.com",
];

export default function FeedPage() {
  const {
    feed, feedLoading, feedHasMore, platformFilter, locale,
    fetchFeed, fetchMore, setPlatformFilter, setLocale, resetFeed, refreshFeed,
  } = useStore();

  const observerRef = useRef<HTMLDivElement>(null);
  const urlInputRef = useRef<UrlInputHandle>(null);
  const isAtTopRef = useRef(true);

  useEffect(() => { resetFeed(); fetchFeed(); }, []);
  useEffect(() => { resetFeed(); fetchFeed(); }, [platformFilter]);

  // Infinite scroll observer
  useEffect(() => {
    const node = observerRef.current;
    if (!node) return;
    const obs = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && feedHasMore && !feedLoading) fetchMore();
    }, { threshold: 0.1 });
    obs.observe(node);
    return () => obs.disconnect();
  }, [feedHasMore, feedLoading, fetchMore]);

  // Task 4: Auto-refresh feed every 15 seconds when at top of page
  useEffect(() => {
    const handleScroll = () => {
      isAtTopRef.current = window.scrollY < 200;
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    const interval = setInterval(() => {
      if (isAtTopRef.current) {
        refreshFeed();
      }
    }, 15000);
    return () => {
      window.removeEventListener("scroll", handleScroll);
      clearInterval(interval);
    };
  }, [refreshFeed]);

  // Task 5: Keyboard shortcuts
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    // Don't trigger when typing in input/textarea
    const tag = (e.target as HTMLElement).tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") {
      if (e.key === "Escape") {
        urlInputRef.current?.blur();
      }
      return;
    }
    if (e.key === "/") {
      e.preventDefault();
      urlInputRef.current?.focus();
    }
  }, []);

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  // Task 6: Handle suggested URL click
  const handleSuggestedUrl = (url: string) => {
    urlInputRef.current?.setUrlAndSubmit(url);
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      {/* Header */}
      <header className="py-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-accent uppercase tracking-wider" data-testid="masthead">
              {t("masthead")}
            </h1>
            <p className="text-[10px] sm:text-xs text-muted uppercase tracking-widest mt-1">
              {t("subtitle_line")}
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs text-muted">
            <span className="live-dot" />
            <span>{t("live")}</span>
          </div>
        </div>
        <div className="h-[2px] bg-accent" />

        {/* Locale */}
        <div className="flex gap-2 mt-3">
          {(Object.keys(localeLabels) as Locale[]).map((l) => (
            <button
              key={l}
              onClick={() => setLocale(l)}
              className={`text-xs px-2 py-0.5 font-mono uppercase ${
                locale === l ? "text-accent border border-accent" : "text-muted border border-border hover:border-accent hover:text-accent"
              }`}
            >
              {l}
            </button>
          ))}
        </div>
      </header>

      {/* URL Input */}
      <section className="mb-6"><UrlInput ref={urlInputRef} /></section>

      {/* Filters — horizontally scrollable on mobile */}
      <div
        className="flex items-center gap-2 overflow-x-auto scrollbar-hide pb-2 mb-4"
        data-testid="platform-filters"
      >
        {FILTERS.map((f) => (
          <button
            key={f.key}
            onClick={() => setPlatformFilter(f.key)}
            className={`filter-pill whitespace-nowrap flex-shrink-0 ${platformFilter === f.key ? "filter-pill-active" : ""}`}
          >
            {t(f.label as Parameters<typeof t>[0])}
          </button>
        ))}
      </div>

      {/* Nav */}
      <div className="flex justify-between items-center mb-4 gap-2">
        <span className="text-[10px] text-muted uppercase tracking-widest font-mono hidden sm:inline">
          {t("press_search")}
        </span>
        <div className="flex gap-2 ml-auto">
          <Link href="/" className="text-xs text-muted hover:text-accent border border-border px-3 py-1 uppercase tracking-wider hover:border-accent transition-colors">
            ?
          </Link>
          <Link href="/top" className="text-xs text-muted hover:text-accent border border-border px-3 py-1 uppercase tracking-wider hover:border-accent transition-colors">
            {t("leaderboard_link")} &rarr;
          </Link>
        </div>
      </div>

      {/* Feed */}
      <div className="flex flex-col gap-3" data-testid="feed-list">
        {feed.map((audit) => <AuditCard key={audit.id} audit={audit} />)}
      </div>

      {feedLoading && <p className="text-center text-accent py-8 animate-pulse font-mono">LOADING...</p>}

      {/* Task 6: Empty state */}
      {!feedLoading && feed.length === 0 && (
        <div className="text-center py-16" data-testid="empty-state">
          <p className="font-mono text-sm text-muted mb-2">// NO AUDITS YET</p>
          <p className="font-mono text-xs text-muted mb-6">// PASTE A URL ABOVE TO START YOUR FIRST AUDIT</p>
          <p className="font-mono text-xs text-muted mb-3">// TRY:</p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-2">
            {SUGGESTED_URLS.map((url) => (
              <button
                key={url}
                onClick={() => handleSuggestedUrl(url)}
                className="font-mono text-xs text-accent hover:text-bg hover:bg-accent border border-border hover:border-accent px-3 py-1.5 transition-colors uppercase"
                data-testid="suggested-url"
              >
                {url}
              </button>
            ))}
          </div>
        </div>
      )}

      {feedHasMore && <div ref={observerRef} className="h-10" />}
      {feedHasMore && !feedLoading && feed.length > 0 && (
        <div className="text-center py-4">
          <button onClick={fetchMore} className="filter-pill hover:filter-pill-active">{t("load_more")}</button>
        </div>
      )}

      <footer className="text-center py-8 mt-8 border-t border-border">
        <p className="text-[10px] text-muted uppercase tracking-widest">{t("footer")}</p>
      </footer>
    </div>
  );
}
