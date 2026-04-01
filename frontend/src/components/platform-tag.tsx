"use client";

const platformLabels: Record<string, string> = {
  amazon_product: "PRODUCT",
  appstore_app: "APP",
  gplay_app: "APP",
  gmaps_place: "PLACE",
  website: "WEB",
  company: "COMPANY",
};

export function PlatformTag({ platform }: { platform: string }) {
  return (
    <span className="text-[10px] font-mono uppercase tracking-widest text-muted border border-border px-2 py-0.5">
      {platformLabels[platform] || "WEB"}
    </span>
  );
}
