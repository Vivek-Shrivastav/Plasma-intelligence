import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { FieldBadge, SubfieldPill, ConceptPill, DepthBadge, ImportanceBar } from "@/components/Badges";
import FigureGallery from "@/components/FigureGallery";
import Link from "next/link";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function PaperPage({ params }: { params: { id: string } }) {
  let paper;
  try {
    paper = await api.papers.byId(params.id);
  } catch {
    notFound();
  }

  const a = paper.analysis;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10 fade-in">

      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-xs font-sans text-gray-400 mb-6">
        <Link href="/" className="hover:text-gray-700 transition-colors">Today</Link>
        <span>/</span>
        {paper.subfields?.[0] && (
          <>
            <Link href={`/subfields/${paper.subfields[0]}`} className="hover:text-gray-700 transition-colors capitalize">
              {paper.subfields[0].replace(/-/g, " ")}
            </Link>
            <span>/</span>
          </>
        )}
        <span className="text-gray-500 truncate max-w-xs">{paper.title?.slice(0, 50)}…</span>
      </nav>

      {/* Header */}
      <header className="mb-8">
        <div className="flex flex-wrap gap-2 items-center mb-3">
          {paper.field && <FieldBadge field={paper.field} />}
          {paper.technical_depth && <DepthBadge depth={paper.technical_depth} />}
          {a?.literature_context?.positioning && (
            <span className={`text-xs font-sans font-medium px-2.5 py-0.5 rounded-full border ${
              a.literature_context.positioning === "breakthrough"
                ? "bg-red-50 text-red-700 border-red-200"
                : a.literature_context.positioning === "significant"
                ? "bg-amber-50 text-amber-700 border-amber-200"
                : "bg-gray-50 text-gray-600 border-gray-200"
            }`}>
              {a.literature_context.positioning}
            </span>
          )}
        </div>

        {/* Headline */}
        <h1 className="headline-serif text-3xl sm:text-4xl leading-tight text-gray-900 mb-3">
          {paper.headline ?? paper.title}
        </h1>

        {/* Original title if different */}
        {paper.headline && paper.headline !== paper.title && (
          <p className="text-sm text-gray-500 font-sans italic mb-3">
            Original title: {paper.title}
          </p>
        )}

        {/* Meta line */}
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-600 font-sans mb-4">
          <span className="font-medium text-gray-800">
            {paper.authors?.slice(0, 4).join(", ")}{paper.authors?.length > 4 ? ` +${paper.authors.length - 4} more` : ""}
          </span>
          <span className="text-gray-400">·</span>
          <span>{paper.journal}</span>
          <span className="text-gray-400">·</span>
          <span>{formatDate(paper.published_date)}</span>
        </div>

        {/* Importance + links row */}
        <div className="flex items-center gap-4 flex-wrap">
          {paper.importance_score != null && <ImportanceBar score={paper.importance_score} />}
          {paper.paper_url && (
            <a href={paper.paper_url} target="_blank" rel="noopener noreferrer"
               className="text-xs font-sans font-medium text-blue-700 hover:underline">
              View paper ↗
            </a>
          )}
          {paper.arxiv_id && (
            <a href={`https://arxiv.org/abs/${paper.arxiv_id}`} target="_blank" rel="noopener noreferrer"
               className="text-xs font-sans font-medium text-blue-700 hover:underline">
              arXiv:{paper.arxiv_id} ↗
            </a>
          )}
          {paper.doi && (
            <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noopener noreferrer"
               className="text-xs font-sans font-medium text-blue-700 hover:underline">
              DOI ↗
            </a>
          )}
        </div>
      </header>

      <hr className="border-gray-200 mb-8" />

      {/* Two-column layout: main + sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">

        {/* Main column */}
        <div className="lg:col-span-2 space-y-8">

          {/* Short summary */}
          {paper.short_summary && (
            <section>
              <p className="text-lg font-sans text-gray-700 leading-relaxed border-l-4 border-gray-300 pl-4 italic">
                {paper.short_summary}
              </p>
            </section>
          )}

          {/* Detailed summary */}
          {a?.detailed_summary && (
            <section>
              <h2 className="headline-serif text-xl text-gray-900 mb-3">Analysis</h2>
              <p className="drop-cap prose-plasma text-base leading-relaxed text-gray-800">
                {a.detailed_summary}
              </p>
            </section>
          )}

          {/* Figures */}
          {paper.figures && paper.figures.length > 0 && (
            <section>
              <h2 className="headline-serif text-xl text-gray-900 mb-1">Figures</h2>
              <p className="text-xs text-gray-400 font-sans mb-2">Click any figure to enlarge</p>
              <FigureGallery figures={paper.figures} />
            </section>
          )}

          {/* Key contributions */}
          {a?.key_contributions && a.key_contributions.length > 0 && (
            <section>
              <h2 className="headline-serif text-xl text-gray-900 mb-3">Key contributions</h2>
              <ul className="space-y-2">
                {a.key_contributions.map((c, i) => (
                  <li key={i} className="flex gap-3 text-sm font-sans text-gray-700 leading-relaxed">
                    <span className="shrink-0 w-5 h-5 rounded-full bg-gray-900 text-white text-xs flex items-center justify-center font-semibold mt-0.5">{i + 1}</span>
                    {c}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Open problems */}
          {a?.open_problems && a.open_problems.length > 0 && (
            <section>
              <h2 className="headline-serif text-xl text-gray-900 mb-3">Open problems identified</h2>
              <div className="space-y-2">
                {a.open_problems.map((op, i) => (
                  <div key={i} className="flex gap-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <span className="text-amber-500 mt-0.5 shrink-0">?</span>
                    <p className="text-sm font-sans text-amber-900 leading-relaxed">{op}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Abstract */}
          <section>
            <h2 className="headline-serif text-xl text-gray-900 mb-3">Abstract</h2>
            <p className="text-sm font-sans text-gray-600 leading-relaxed bg-gray-50 p-4 rounded-xl border border-gray-200 italic">
              {paper.abstract}
            </p>
          </section>
        </div>

        {/* Sidebar */}
        <aside className="space-y-6">

          {/* Literature context */}
          {a?.literature_context && (
            <div className="bg-white border border-gray-200 rounded-xl p-4 space-y-4">
              <h3 className="headline-serif text-base text-gray-900">Literature context</h3>
              {a.literature_context.historical_background && (
                <div>
                  <p className="text-xs font-sans font-semibold text-gray-500 uppercase tracking-wider mb-1">Historical background</p>
                  <p className="text-xs font-sans text-gray-600 leading-relaxed">{a.literature_context.historical_background}</p>
                </div>
              )}
              {a.literature_context.recent_trends && (
                <div>
                  <p className="text-xs font-sans font-semibold text-gray-500 uppercase tracking-wider mb-1">Recent trends</p>
                  <p className="text-xs font-sans text-gray-600 leading-relaxed">{a.literature_context.recent_trends}</p>
                </div>
              )}
            </div>
          )}

          {/* Methods */}
          {a?.methods_used && a.methods_used.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="headline-serif text-base text-gray-900 mb-2">Methods</h3>
              <div className="flex flex-wrap gap-1.5">
                {a.methods_used.map(m => (
                  <span key={m} className="text-xs font-sans bg-slate-100 text-slate-700 px-2 py-1 rounded-lg">{m}</span>
                ))}
              </div>
            </div>
          )}

          {/* Subfields */}
          {paper.subfields && paper.subfields.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="headline-serif text-base text-gray-900 mb-2">Subfields</h3>
              <div className="flex flex-wrap gap-1.5">
                {paper.subfields.map(s => (
                  <Link key={s} href={`/subfields/${s}`}>
                    <SubfieldPill name={s} />
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Concepts */}
          {paper.concepts_detected && paper.concepts_detected.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="headline-serif text-base text-gray-900 mb-2">Concepts detected</h3>
              <div className="flex flex-wrap gap-1.5">
                {paper.concepts_detected.map(c => <ConceptPill key={c} name={c} />)}
              </div>
            </div>
          )}

          {/* Keywords */}
          {paper.keywords && paper.keywords.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="headline-serif text-base text-gray-900 mb-2">Keywords</h3>
              <div className="flex flex-wrap gap-1.5">
                {paper.keywords.map(k => (
                  <span key={k} className="text-xs font-sans text-gray-600 bg-gray-100 px-2 py-0.5 rounded">{k}</span>
                ))}
              </div>
            </div>
          )}

          {/* Confidence */}
          {a?.classification_confidence && (
            <div className="bg-white border border-gray-200 rounded-xl p-4">
              <h3 className="headline-serif text-base text-gray-900 mb-1">Classification confidence</h3>
              <span className={`text-xs font-sans font-medium px-2 py-0.5 rounded-full border ${
                a.classification_confidence === "high" ? "bg-green-50 text-green-700 border-green-200"
                : a.classification_confidence === "medium" ? "bg-amber-50 text-amber-700 border-amber-200"
                : "bg-red-50 text-red-700 border-red-200"
              }`}>
                {a.classification_confidence}
              </span>
            </div>
          )}

        </aside>
      </div>
    </div>
  );
}
