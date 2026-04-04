"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, Paper } from "@/lib/api";
import PaperCard from "@/components/PaperCard";
import Link from "next/link";

const SUBFIELD_NAMES: Record<string, string> = {
  "magnetic-reconnection": "Magnetic Reconnection",
  "plasma-turbulence": "Plasma Turbulence",
  "two-stream-instability": "Two-Stream Instability",
  "tokamak": "Tokamak Physics",
  "stellarator": "Stellarator Physics",
  "solar-wind": "Solar Wind Plasma",
  "magnetosphere": "Magnetospheric Physics",
  "mhd-waves": "MHD Waves",
  "kinetic-effects": "Kinetic Effects",
  "plasma-heating": "Plasma Heating",
  "confinement": "Plasma Confinement",
  "transport": "Plasma Transport",
  "shocks": "Collisionless Shocks",
  "accretion-disks": "Accretion Disk Plasma",
  "pic-simulations": "PIC Simulations",
  "drift-waves": "Drift Waves",
  "plasma-instability": "Plasma Instabilities",
  "diagnostics": "Plasma Diagnostics",
};

export default function SubfieldPage() {
  const params = useParams();
  const slug = params.slug as string;
  const name = SUBFIELD_NAMES[slug] ?? slug;

  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(180);
  const [minScore, setMinScore] = useState(1);
  const [sortBy, setSortBy] = useState<"score" | "date">("score");

  useEffect(() => {
    setLoading(true);
    api.subfields.feed(slug, days)
      .then(d => setPapers(d.papers))
      .catch(() => setPapers([]))
      .finally(() => setLoading(false));
  }, [slug, days]);

  const filtered = papers
    .filter(p => (p.importance_score ?? 0) >= minScore)
    .sort((a, b) =>
      sortBy === "score"
        ? (b.importance_score ?? 0) - (a.importance_score ?? 0)
        : new Date(b.published_date).getTime() - new Date(a.published_date).getTime()
    );

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 fade-in">

      {/* Breadcrumb */}
      <nav className="flex gap-2 text-xs font-sans text-gray-400 mb-4">
        <Link href="/" className="hover:text-gray-700">Today</Link>
        <span>/</span>
        <Link href="/subfields" className="hover:text-gray-700">Subfields</Link>
        <span>/</span>
        <span className="text-gray-600">{name}</span>
      </nav>

      {/* Header */}
      <div className="mb-6 pb-4 border-b border-gray-200">
        <div className="flex items-start justify-between flex-wrap gap-3">
          <div>
            <h1 className="headline-serif text-3xl text-gray-900">{name}</h1>
            <p className="text-sm text-gray-500 font-sans mt-1">{filtered.length} papers · last {days} days</p>
          </div>
          <Link
            href={`/subfields/${slug}/literature`}
            className="text-sm font-sans font-medium text-purple-700 border border-purple-200 bg-purple-50 px-4 py-2 rounded-lg hover:bg-purple-100 transition-colors"
          >
            Literature review →
          </Link>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 mt-4">
          <div className="flex items-center gap-2">
            <label className="text-xs font-sans text-gray-500">Date range</label>
            <select
              value={days}
              onChange={e => setDays(Number(e.target.value))}
              className="text-xs font-sans border border-gray-200 rounded-lg px-2 py-1.5 bg-white"
            >
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 3 months</option>
              <option value={180}>Last 6 months</option>
              <option value={365}>Last year</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-xs font-sans text-gray-500">Min. score</label>
            <select
              value={minScore}
              onChange={e => setMinScore(Number(e.target.value))}
              className="text-xs font-sans border border-gray-200 rounded-lg px-2 py-1.5 bg-white"
            >
              {[1,2,3,4,5,6,7,8].map(v => (
                <option key={v} value={v}>{v}+</option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-xs font-sans text-gray-500">Sort by</label>
            <select
              value={sortBy}
              onChange={e => setSortBy(e.target.value as "score" | "date")}
              className="text-xs font-sans border border-gray-200 rounded-lg px-2 py-1.5 bg-white"
            >
              <option value="score">Importance</option>
              <option value="date">Date</option>
            </select>
          </div>
        </div>
      </div>

      {loading && (
        <div className="space-y-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-24 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      )}

      {!loading && filtered.length === 0 && (
        <div className="text-center py-16">
          <div className="text-4xl mb-3">⚛</div>
          <p className="text-gray-500 font-sans text-sm">No papers found for these filters.</p>
          <p className="text-gray-400 font-sans text-xs mt-1">Try extending the date range or lowering the minimum score.</p>
        </div>
      )}

      {!loading && filtered.length > 0 && (
        <div className="space-y-3">
          {filtered.map(p => (
            <PaperCard key={p.id} paper={p} variant="card" />
          ))}
        </div>
      )}
    </div>
  );
}
