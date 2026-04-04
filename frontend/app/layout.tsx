import type { Metadata } from "next";
import "./globals.css";
import Nav from "@/components/Nav";

export const metadata: Metadata = {
  title: "Plasma Intelligence — Daily Research Digest",
  description:
    "Automated daily digest of plasma physics research across 18 journals. Headlines, summaries, figures, literature reviews, and open problems — updated every morning.",
  keywords: ["plasma physics", "tokamak", "magnetic reconnection", "fusion", "research digest"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css"
        />
      </head>
      <body className="min-h-screen">
        <Nav />
        <main>{children}</main>
        <footer className="border-t border-gray-200 mt-16 py-8 text-center text-xs text-gray-400 font-sans">
          <p>Plasma Intelligence · Updated daily at 02:00 UTC · Papers from 18 journals & arXiv</p>
          <p className="mt-1">Analysis powered by Claude · Not affiliated with any journal publisher</p>
        </footer>
      </body>
    </html>
  );
}
