import { create } from "zustand";
import {
  api,
  type AuditCard,
  type AuditDetail,
  type Company,
  type CompanyDetail,
} from "./api";
import { type Locale, getLocale, setLocale as setI18nLocale } from "./i18n";

interface Store {
  // Feed
  feed: AuditCard[];
  feedPage: number;
  feedHasMore: boolean;
  feedLoading: boolean;
  platformFilter: string;
  severityFilter: string;

  // Audit detail
  currentAudit: AuditDetail | null;

  // Company
  currentCompany: CompanyDetail | null;
  companyAudits: AuditCard[];
  companyAuditsPage: number;
  companyAuditsHasMore: boolean;

  // Leaderboard
  leaderboard: { best: Company[]; worst: Company[] };

  // i18n
  locale: Locale;

  // Actions
  fetchFeed: () => Promise<void>;
  fetchMore: () => Promise<void>;
  refreshFeed: () => Promise<void>;
  fetchAudit: (id: number) => Promise<void>;
  fetchCompany: (slug: string) => Promise<void>;
  fetchCompanyAudits: (slug: string, page?: number) => Promise<void>;
  fetchLeaderboard: () => Promise<void>;
  submitAudit: (url: string) => Promise<number>;
  setLocale: (l: Locale) => void;
  setPlatformFilter: (p: string) => void;
  setSeverityFilter: (s: string) => void;
  resetFeed: () => void;
}

export const useStore = create<Store>((set, get) => ({
  feed: [],
  feedPage: 1,
  feedHasMore: true,
  feedLoading: false,
  platformFilter: "",
  severityFilter: "",

  currentAudit: null,

  currentCompany: null,
  companyAudits: [],
  companyAuditsPage: 1,
  companyAuditsHasMore: true,

  leaderboard: { best: [], worst: [] },

  locale: typeof window !== "undefined" ? getLocale() : "en",

  fetchFeed: async () => {
    set({ feedLoading: true });
    try {
      const { platformFilter, severityFilter } = get();
      const res = await api.getFeed(
        1,
        20,
        platformFilter || undefined,
        severityFilter || undefined
      );
      set({
        feed: res.items,
        feedPage: 1,
        feedHasMore: res.has_more,
      });
    } finally {
      set({ feedLoading: false });
    }
  },

  fetchMore: async () => {
    const { feedPage, feedHasMore, feedLoading, platformFilter, severityFilter, feed } = get();
    if (!feedHasMore || feedLoading) return;
    set({ feedLoading: true });
    try {
      const nextPage = feedPage + 1;
      const res = await api.getFeed(
        nextPage,
        20,
        platformFilter || undefined,
        severityFilter || undefined
      );
      set({
        feed: [...feed, ...res.items],
        feedPage: nextPage,
        feedHasMore: res.has_more,
      });
    } finally {
      set({ feedLoading: false });
    }
  },

  refreshFeed: async () => {
    try {
      const { platformFilter, severityFilter, feed } = get();
      const res = await api.getFeed(
        1,
        20,
        platformFilter || undefined,
        severityFilter || undefined
      );
      // Prepend new items that don't already exist in the feed
      const existingIds = new Set(feed.map((a) => a.id));
      const newItems = res.items.filter((item) => !existingIds.has(item.id));
      if (newItems.length > 0) {
        // Also update existing items (status may have changed)
        const updatedMap = new Map(res.items.map((item) => [item.id, item]));
        const updatedFeed = feed.map((item) => updatedMap.get(item.id) ?? item);
        set({ feed: [...newItems, ...updatedFeed] });
      } else {
        // Still update statuses of existing items
        const updatedMap = new Map(res.items.map((item) => [item.id, item]));
        const updatedFeed = feed.map((item) => updatedMap.get(item.id) ?? item);
        set({ feed: updatedFeed });
      }
    } catch {
      // Silent fail for background refresh
    }
  },

  fetchAudit: async (id: number) => {
    // Don't reset to null — prevents flash on auto-refresh
    const audit = await api.getAudit(id);
    set({ currentAudit: audit });
  },

  fetchCompany: async (slug: string) => {
    set({ currentCompany: null, companyAudits: [], companyAuditsPage: 1, companyAuditsHasMore: true });
    const [company, auditsRes] = await Promise.all([
      api.getCompany(slug),
      api.getCompanyAudits(slug, 1),
    ]);
    set({
      currentCompany: company,
      companyAudits: auditsRes.items,
      companyAuditsPage: 1,
      companyAuditsHasMore: auditsRes.has_more,
    });
  },

  fetchCompanyAudits: async (slug: string, page?: number) => {
    const { companyAuditsPage, companyAudits } = get();
    const nextPage = page ?? companyAuditsPage + 1;
    const res = await api.getCompanyAudits(slug, nextPage);
    set({
      companyAudits: nextPage === 1 ? res.items : [...companyAudits, ...res.items],
      companyAuditsPage: nextPage,
      companyAuditsHasMore: res.has_more,
    });
  },

  fetchLeaderboard: async () => {
    const [best, worst] = await Promise.all([
      api.getCompanies("best", 20),
      api.getCompanies("worst", 20),
    ]);
    set({ leaderboard: { best, worst } });
  },

  submitAudit: async (url: string) => {
    const res = await api.submitAudit(url);
    return res.audit_id;
  },

  setLocale: (locale: Locale) => {
    setI18nLocale(locale);
    set({ locale });
  },

  setPlatformFilter: (platformFilter: string) => {
    set({ platformFilter });
  },

  setSeverityFilter: (severityFilter: string) => {
    set({ severityFilter });
  },

  resetFeed: () => {
    set({ feed: [], feedPage: 1, feedHasMore: true });
  },
}));
