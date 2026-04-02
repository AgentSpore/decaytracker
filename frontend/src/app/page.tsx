"use client";

import Link from "next/link";
import { useStore } from "@/lib/store";
import { t, localeLabels, type Locale } from "@/lib/i18n";

const CONTENT = {
  en: {
    hero_title: "THE TRUST FEED",
    hero_sub: "AI audits everything you buy",
    hero_desc: "Paste any URL — get an instant AI-powered trust audit. Fake reviews, dark patterns, hidden fees, enshittification — we detect it all.",
    how_title: "HOW IT WORKS",
    steps: [
      { num: "01", title: "PASTE URL", desc: "Drop any link — Amazon product, App Store app, company website, Google Maps place. Any URL works." },
      { num: "02", title: "AI SCANS", desc: "Our agent scrapes the page, runs 5 Google searches for fraud signals, checks Trustpilot, analyzes reviews for bots." },
      { num: "03", title: "GET REPORT", desc: "Trust score 0-100, detailed findings with evidence links, severity ratings. Published to the public feed." },
    ],
    what_title: "WHAT WE DETECT",
    detects: [
      { icon: "!!", label: "FAKE REVIEWS", desc: "Bot-generated reviews, purchased ratings, review farms, incentivized feedback" },
      { icon: "$$", label: "PRICE MANIPULATION", desc: "Fake discounts, anchor pricing, bait-and-switch, hidden fees at checkout" },
      { icon: "##", label: "DARK PATTERNS", desc: "Manipulative UI, forced opt-ins, shame-clicking, hard-to-cancel subscriptions" },
      { icon: "~~", label: "ENSHITTIFICATION", desc: "Products getting worse over time — feature removal, price hikes, ad injection" },
      { icon: "**", label: "ASTROTURFING", desc: "Fake grassroots campaigns, paid opinions disguised as organic, sockpuppet accounts" },
      { icon: "++", label: "DATA HARVESTING", desc: "Excessive data collection, selling user data, tracking without consent" },
    ],
    companies_title: "COMPANY TRUST SCORES",
    companies_desc: "Every audit links to a company. Audits accumulate — forming a live trust rating. See who's trustworthy and who's not on the leaderboard.",
    free_title: "FREE & PUBLIC",
    free_desc: "No registration. No tracking. No ads. All audits are public. The feed belongs to everyone.",
    cta: "START AUDITING",
    stats_audits: "AUDITS COMPLETED",
    stats_companies: "COMPANIES TRACKED",
    stats_findings: "ISSUES DETECTED",
  },
  ru: {
    hero_title: "ЛЕНТА ДОВЕРИЯ",
    hero_sub: "ИИ проверяет всё что вы покупаете",
    hero_desc: "Вставьте любую ссылку — получите мгновенный ИИ-аудит доверия. Фейковые отзывы, тёмные паттерны, скрытые платежи, деградация продуктов — мы обнаруживаем всё.",
    how_title: "КАК ЭТО РАБОТАЕТ",
    steps: [
      { num: "01", title: "ВСТАВЬТЕ URL", desc: "Любая ссылка — товар на Amazon, приложение в App Store, сайт компании, место на Google Maps." },
      { num: "02", title: "ИИ СКАНИРУЕТ", desc: "Агент сканирует страницу, делает 5 поисковых запросов на мошенничество, проверяет Trustpilot, анализирует отзывы на ботов." },
      { num: "03", title: "ПОЛУЧИТЕ ОТЧЁТ", desc: "Рейтинг доверия 0-100, детальные находки со ссылками на доказательства. Публикуется в общую ленту." },
    ],
    what_title: "ЧТО МЫ ОБНАРУЖИВАЕМ",
    detects: [
      { icon: "!!", label: "ФЕЙКОВЫЕ ОТЗЫВЫ", desc: "Бот-отзывы, купленные рейтинги, фермы отзывов, мотивированные отклики" },
      { icon: "$$", label: "МАНИПУЛЯЦИЯ ЦЕНАМИ", desc: "Фейковые скидки, якорное ценообразование, скрытые платежи на кассе" },
      { icon: "##", label: "ТЁМНЫЕ ПАТТЕРНЫ", desc: "Манипулятивный интерфейс, принудительные подписки, невозможность отписаться" },
      { icon: "~~", label: "ДЕГРАДАЦИЯ ПРОДУКТОВ", desc: "Ухудшение сервисов — удаление функций, рост цен, добавление рекламы" },
      { icon: "**", label: "АСТРОТУРФИНГ", desc: "Фейковые кампании, платные мнения под видом органических, подставные аккаунты" },
      { icon: "++", label: "СБОР ДАННЫХ", desc: "Чрезмерный сбор данных, продажа данных, слежка без согласия" },
    ],
    companies_title: "РЕЙТИНГИ КОМПАНИЙ",
    companies_desc: "Каждый аудит привязан к компании. Аудиты накапливаются — формируя живой рейтинг доверия. Смотрите кто честен, а кто нет.",
    free_title: "БЕСПЛАТНО И ПУБЛИЧНО",
    free_desc: "Без регистрации. Без трекинга. Без рекламы. Все аудиты публичны. Лента принадлежит всем.",
    cta: "НАЧАТЬ ПРОВЕРКУ",
    stats_audits: "АУДИТОВ ЗАВЕРШЕНО",
    stats_companies: "КОМПАНИЙ ОТСЛЕЖИВАЕТСЯ",
    stats_findings: "ПРОБЛЕМ ОБНАРУЖЕНО",
  },
  cn: {
    hero_title: "信任动态",
    hero_sub: "AI审核您购买的一切",
    hero_desc: "粘贴任何链接——获得即时AI信任审核。虚假评论、暗黑模式、隐藏费用、产品劣化——我们全部检测。",
    how_title: "工作原理",
    steps: [
      { num: "01", title: "粘贴链接", desc: "任何链接——亚马逊产品、App Store应用、公司网站、Google地图地点。" },
      { num: "02", title: "AI扫描", desc: "代理扫描页面，进行5次欺诈信号搜索，检查Trustpilot，分析评论中的机器人。" },
      { num: "03", title: "获取报告", desc: "信任评分0-100，带证据链接的详细发现。发布到公共动态。" },
    ],
    what_title: "我们检测什么",
    detects: [
      { icon: "!!", label: "虚假评论", desc: "机器人评论、购买评分、评论农场、激励反馈" },
      { icon: "$$", label: "价格操纵", desc: "虚假折扣、锚定定价、隐藏费用" },
      { icon: "##", label: "暗黑模式", desc: "操纵性界面、强制订阅、难以取消" },
      { icon: "~~", label: "产品劣化", desc: "服务恶化——删除功能、涨价、插入广告" },
      { icon: "**", label: "水军营销", desc: "虚假草根活动、伪装成有机的付费意见" },
      { icon: "++", label: "数据收割", desc: "过度数据收集、出售用户数据、未经同意跟踪" },
    ],
    companies_title: "公司信任评分",
    companies_desc: "每次审核关联一家公司。审核累积——形成实时信任评级。在排行榜查看谁值得信任。",
    free_title: "免费且公开",
    free_desc: "无需注册。无追踪。无广告。所有审核公开。动态属于每个人。",
    cta: "开始审核",
    stats_audits: "已完成审核",
    stats_companies: "已追踪公司",
    stats_findings: "已发现问题",
  },
};

export default function AboutPage() {
  const { locale, setLocale } = useStore();
  const c = CONTENT[locale] || CONTENT.en;

  return (
    <div className="max-w-3xl mx-auto px-4 py-6">
      {/* Language */}
      <div className="flex gap-2 mb-8">
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

      {/* Hero */}
      <header className="py-12 mb-8">
        <h1 className="text-3xl md:text-5xl font-bold text-accent uppercase tracking-wider leading-tight">
          {c.hero_title}
        </h1>
        <p className="text-lg md:text-xl text-muted mt-4 font-mono">{c.hero_sub}</p>
        <p className="text-sm text-muted mt-4 leading-relaxed max-w-xl">{c.hero_desc}</p>
        <div className="h-[2px] bg-accent mt-8" />
      </header>

      {/* How it works */}
      <section className="mb-12">
        <h2 className="text-xs text-accent uppercase tracking-widest font-bold mb-6">{c.how_title}</h2>
        <div className="flex flex-col gap-6">
          {c.steps.map((step) => (
            <div key={step.num} className="flex gap-4">
              <span className="text-3xl font-bold text-accent/30 font-mono flex-shrink-0 w-12">{step.num}</span>
              <div>
                <h3 className="font-bold text-sm uppercase tracking-wider mb-1">{step.title}</h3>
                <p className="text-sm text-muted leading-relaxed">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* What we detect */}
      <section className="mb-12">
        <h2 className="text-xs text-accent uppercase tracking-widest font-bold mb-6">{c.what_title}</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {c.detects.map((d) => (
            <div key={d.label} className="border border-border p-4 bg-card">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-accent font-bold font-mono text-sm">{d.icon}</span>
                <span className="text-xs font-bold uppercase tracking-wider">{d.label}</span>
              </div>
              <p className="text-xs text-muted leading-relaxed">{d.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Companies */}
      <section className="mb-12 border border-accent p-6">
        <h2 className="text-xs text-accent uppercase tracking-widest font-bold mb-3">{c.companies_title}</h2>
        <p className="text-sm text-muted leading-relaxed">{c.companies_desc}</p>
      </section>

      {/* Free */}
      <section className="mb-12">
        <h2 className="text-xs text-accent uppercase tracking-widest font-bold mb-3">{c.free_title}</h2>
        <p className="text-sm text-muted leading-relaxed">{c.free_desc}</p>
      </section>

      {/* CTA */}
      <div className="text-center py-8">
        <Link
          href="/feed"
          className="inline-block bg-accent text-bg px-8 py-4 font-mono font-bold text-sm uppercase tracking-widest hover:bg-accent2 transition-colors"
        >
          {c.cta} →
        </Link>
      </div>

      <footer className="text-center py-8 border-t border-border">
        <p className="text-[10px] text-muted uppercase tracking-widest">{t("footer")}</p>
      </footer>
    </div>
  );
}
