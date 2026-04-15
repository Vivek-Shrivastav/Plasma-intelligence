import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import PaperCard from "@/components/PaperCard";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  let data: Awaited<ReturnType<typeof api.papers.today>> | null = null;
  let error = false;

  try {
    data = await api.papers.today();
  } catch {
    error = true;
  }

  const papers = data?.papers ?? [];
  const dateStr = data?.date ?? new Date().toISOString().split("T")[0];
  const topPapers = papers.slice(0, 3);
  const restPapers = papers.slice(3);

  // Group by field for the field nav strip
  const fields = Array.from(new Set(papers.map(p => p.field).filter(Boolean))) as string[];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">

      {/* Newspaper masthead */}
      <div className="text-center mb-6">
        <div className="masthead-rule mb-3" />
        <div className="flex items-center justify-between text-xs font-sans text-gray-500 mb-2">
          <span>Est. 2025 · 18 Journals · arXiv</span>
          <span className="font-semibold text-gray-700 text-sm">{formatDate(dateStr)}</span>
          <span>{papers.length} papers today</span>
        </div>
        <h1 className="headline-serif text-4xl sm:text-5xl tracking-tight text-gray-900">
          Plasma Intelligence
        </h1>
        <p className="text-sm text-gray-500 font-sans mt-1 italic">
          The daily digest of plasma physics research
        </p>
        <div className="masthead-rule mt-3" />
      </div>

      {/* Field navigation strip */}
      {fields.length > 0 && (
        <div className="flex gap-2 flex-wrap mb-6 pb-4 border-b border-gray-200">
          {fields.map(f => (
            <span key={f} className="text-xs font-sans bg-gray-100 text-gray-700 px-3 py-1 rounded-full">
              {f}
            </span>
          ))}
          <Link href="/subfields" className="text-xs font-sans bg-gray-900 text-white px-3 py-1 rounded-full hover:bg-gray-700 transition-colors ml-auto">
            Browse subfields →
          </Link>
        </div>
      )}

      {error && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 text-center mb-8">
          <p className="text-amber-800 font-sans text-sm font-medium">Unable to reach the API server.</p>
          <p className="text-amber-600 font-sans text-xs mt-1">Make sure the backend is running at <code>{process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}</code></p>
        </div>
      )}

      {!error && papers.length === 0 && (
        <div className="text-center py-20">
          <div className="text-6xl mb-4">⚛</div>
          <h2 className="headline-serif text-2xl text-gray-700 mb-2">No papers yet for today</h2>
          <p className="text-gray-500 font-sans text-sm max-w-md mx-auto">
            The daily fetch runs at 02:00 UTC. Run <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">scripts/backfill.py</code> to populate historical data.
          </p>
        </div>
      )}

      {papers.length > 0 && (
        <>
          {/* Top stories — 3-column newspaper layout */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {topPapers.map((paper, i) => (
              <div
                key={paper.id}
                className={`${i === 0 ? "md:col-span-1 col-rule pr-6" : ""} ${i === 2 ? "border-l border-gray-200 pl-6" : ""} ${i === 1 ? "md:col-span-1 px-0 md:border-l md:border-gray-200 md:pl-6" : ""}`}
              >
                <PaperCard paper={paper} variant="headline" />
              </div>
            ))}
          </div>

          {restPapers.length > 0 && (
            <>
              <div className="flex items-center gap-3 mb-4">
                <div className="h-px bg-gray-200 flex-1" />
                <span className="text-xs font-sans font-semibold text-gray-500 uppercase tracking-widest">More Papers</span>
                <div className="h-px bg-gray-200 flex-1" />
              </div>

              {/* Two-column compact list */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-0 mb-8">
                {restPapers.map((paper) => (
                  <div key={paper.id} className="md:odd:pr-6 md:even:pl-6 md:even:border-l md:even:border-gray-200">
                    <PaperCard paper={paper} variant="compact" />
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Bottom nav */}
          <div className="flex gap-4 justify-center pt-6 border-t border-gray-200">
            <Link href="/subfields" className="font-sans text-sm text-gray-600 hover:text-gray-900 transition-colors">
              Explore subfields →
            </Link>
            <span className="text-gray-300">|</span>
            <Link href="/open-problems" className="font-sans text-sm text-gray-600 hover:text-gray-900 transition-colors">
              Open problems →
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
