import { api } from "@/lib/api";
import { URGENCY_COLORS } from "@/lib/utils";
import { cn } from "@/lib/utils";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function OpenProblemsPage() {
  let data: Awaited<ReturnType<typeof api.openProblems.clusters>> | null = null;
  try {
    data = await api.openProblems.clusters();
  } catch {
    data = null;
  }

  const clusters = data?.clusters ?? [];
  const high = clusters.filter(c => c.urgency === "high");
  const medium = clusters.filter(c => c.urgency === "medium");
  const low = clusters.filter(c => c.urgency === "low");

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 fade-in">

      {/* Header */}
      <div className="mb-8">
        <h1 className="headline-serif text-4xl text-gray-900 mb-2">Open Problems</h1>
        <p className="text-sm font-sans text-gray-500 max-w-2xl leading-relaxed">
          Automatically extracted and clustered from papers across all subfields. Updated weekly by synthesizing open problem statements identified during daily paper analysis.
        </p>
        <div className="flex gap-4 mt-3 text-xs font-sans">
          {high.length > 0 && <span className="text-red-600 font-medium">{high.length} high urgency</span>}
          {medium.length > 0 && <span className="text-amber-600 font-medium">{medium.length} medium urgency</span>}
          {low.length > 0 && <span className="text-green-600 font-medium">{low.length} low urgency</span>}
        </div>
      </div>

      {clusters.length === 0 && (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">🔬</div>
          <h2 className="headline-serif text-2xl text-gray-700 mb-2">No clusters yet</h2>
          <p className="text-sm font-sans text-gray-500 max-w-md mx-auto">
            Open problem clusters are synthesized weekly. Once papers are processed, run the weekly synthesis job or wait until Sunday 03:00 UTC.
          </p>
          <code className="block mt-3 bg-gray-100 text-gray-700 text-xs font-mono px-4 py-2 rounded-lg inline-block">
            POST /api/pipeline/run-daily (with admin token)
          </code>
        </div>
      )}

      {clusters.length > 0 && (
        <div className="space-y-10">

          {/* High urgency */}
          {high.length > 0 && (
            <section>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <h2 className="headline-serif text-xl text-gray-900">High urgency</h2>
                <span className="text-xs font-sans text-gray-400">blocking progress across subfields</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {high.map(c => <ClusterCard key={c.id} cluster={c} />)}
              </div>
            </section>
          )}

          {/* Medium urgency */}
          {medium.length > 0 && (
            <section>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-3 h-3 rounded-full bg-amber-400" />
                <h2 className="headline-serif text-xl text-gray-900">Medium urgency</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {medium.map(c => <ClusterCard key={c.id} cluster={c} />)}
              </div>
            </section>
          )}

          {/* Low urgency */}
          {low.length > 0 && (
            <section>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <h2 className="headline-serif text-xl text-gray-900">Lower priority</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {low.map(c => <ClusterCard key={c.id} cluster={c} />)}
              </div>
            </section>
          )}

        </div>
      )}
    </div>
  );
}

function ClusterCard({ cluster }: { cluster: NonNullable<typeof api.openProblems.clusters extends (...args: any) => Promise<infer R> ? R : never>["clusters"][number] }) {
  const urgencyClass = URGENCY_COLORS[cluster.urgency] ?? "bg-gray-100 text-gray-700";

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-sm transition-shadow">
      <div className="flex items-start justify-between gap-2 mb-3">
        <h3 className="headline-serif text-base text-gray-900 leading-snug">{cluster.theme}</h3>
        <span className={cn("shrink-0 text-xs font-sans font-medium px-2 py-0.5 rounded-full", urgencyClass)}>
          {cluster.urgency}
        </span>
      </div>

      <p className="text-sm font-sans text-gray-600 leading-relaxed mb-3">{cluster.description}</p>

      <div className="flex flex-wrap gap-1.5 mb-3">
        {cluster.subfields?.slice(0, 4).map(s => (
          <Link key={s} href={`/subfields/${s}`}
            className="text-xs font-sans bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full hover:bg-slate-200 transition-colors">
            {s}
          </Link>
        ))}
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-gray-100">
        <div className="flex items-center gap-1">
          <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gray-400 rounded-full"
              style={{ width: `${Math.min(100, (cluster.frequency / 10) * 100)}%` }}
            />
          </div>
          <span className="text-xs font-sans text-gray-500">{cluster.frequency} papers</span>
        </div>
        {cluster.first_appeared && (
          <span className="text-xs font-sans text-gray-400">
            since {cluster.first_appeared?.slice(0, 7)}
          </span>
        )}
      </div>
    </div>
  );
}
