"use client";

import { useState, useCallback, useRef, useImperativeHandle, forwardRef } from "react";
import { toast } from "sonner";
import { useStore } from "@/lib/store";
import { api } from "@/lib/api";
import { t } from "@/lib/i18n";

export interface UrlInputHandle {
  focus: () => void;
  blur: () => void;
  setUrlAndSubmit: (url: string) => void;
}

export const UrlInput = forwardRef<UrlInputHandle>(function UrlInput(_props, ref) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const { fetchFeed, resetFeed } = useStore();

  const handleSubmit = useCallback(async (overrideUrl?: string) => {
    let trimmed = (overrideUrl ?? url).trim();
    if (!trimmed) return;
    // Auto-prepend https:// if no protocol
    if (trimmed && !trimmed.startsWith("http://") && !trimmed.startsWith("https://")) {
      trimmed = "https://" + trimmed;
    }
    setLoading(true);
    try {
      const { audit_id: id } = await api.submitAudit(trimmed);
      setUrl("");
      // Redirect to audit page immediately — user sees live status
      window.location.href = `/audit/${id}`;
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed");
    } finally { setLoading(false); }
  }, [url, fetchFeed, resetFeed]);

  useImperativeHandle(ref, () => ({
    focus: () => inputRef.current?.focus(),
    blur: () => inputRef.current?.blur(),
    setUrlAndSubmit: (newUrl: string) => {
      setUrl(newUrl);
      handleSubmit(newUrl);
    },
  }), [handleSubmit]);

  return (
    <div className="border-2 border-accent bg-card p-4" data-testid="url-input">
      <div className="text-xs text-accent uppercase tracking-wider mb-2 font-bold">
        $ enter url to audit_<span className="inline-block w-2 h-4 bg-accent ml-1 animate-pulse" />
      </div>
      <div className="flex flex-col sm:flex-row gap-0">
        <input
          ref={inputRef}
          type="url"
          inputMode="url"
          autoCapitalize="off"
          autoCorrect="off"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !loading && handleSubmit()}
          placeholder="https://..."
          disabled={loading}
          className="flex-1 bg-bg border border-border px-4 py-3 font-mono text-sm text-text outline-none focus:border-accent disabled:opacity-50"
          data-testid="url-input-field"
        />
        <button
          onClick={() => handleSubmit()}
          disabled={loading || !url.trim()}
          className="w-full sm:w-auto bg-accent text-bg px-6 py-3 font-mono font-bold text-sm uppercase tracking-wider hover:bg-accent2 disabled:opacity-50 transition-colors"
          data-testid="audit-submit-btn"
        >
          {loading ? "..." : t("run_audit")}
        </button>
      </div>
    </div>
  );
});
