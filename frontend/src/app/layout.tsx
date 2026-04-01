import type { Metadata } from "next";
import { Toaster } from "sonner";
import "./globals.css";

export const metadata: Metadata = {
  title: "The Trust Feed — AI audits everything you buy",
  description: "Public feed of AI-powered trust audits. Paste any URL — get instant analysis of fake reviews, dark patterns, and enshittification. DecayTracker v2.",
  openGraph: {
    title: "The Trust Feed",
    description: "AI audits everything you buy. Paste any URL.",
    type: "website",
    siteName: "DecayTracker",
  },
  twitter: {
    card: "summary_large_image",
    title: "The Trust Feed",
    description: "AI audits everything you buy",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-bg text-text font-mono">
        {children}
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: "#141414",
              border: "1px solid #2A2A2A",
              color: "#E0E0E0",
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "13px",
            },
          }}
        />
      </body>
    </html>
  );
}
