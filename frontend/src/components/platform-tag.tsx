"use client";

import { t } from "@/lib/i18n";

export function PlatformTag({ platform }: { platform: string }) {
  const labels: Record<string, () => string> = {
    amazon_product: () => t("platform_product"),
    appstore_app: () => t("platform_app"),
    gplay_app: () => t("platform_app"),
    gmaps_place: () => t("platform_place"),
    website: () => t("platform_web"),
    company: () => t("platform_company"),
  };

  const label = labels[platform]?.() || t("platform_web");

  return (
    <span className="text-[10px] font-mono uppercase tracking-widest text-muted border border-border px-2 py-0.5">
      {label}
    </span>
  );
}
