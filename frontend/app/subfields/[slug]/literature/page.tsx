import { api } from "@/lib/api";
import LitReviewRenderer from "@/components/LitReviewRenderer";
import Link from "next/link";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function LiteraturePage({ params }: { params: { slug: string } }) {
  let review;
  try {
    review = await api.literature.get(params.slug);
  } catch {
    notFound();
  }

  const lastUpdated = review.last_updated
    ? new Date(review.last_updated).toLocaleDateString("en-GB", {
        year: "numeric", month: "long", day: "numeric", hour: "2-digit", minute: "2-digit",
      })
    : null;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10 fade-in">

      {/* Breadcrumb */}
      <nav className="flex gap-2 text-xs font-sans text-gray-400 mb-6">
        <Link href="/" className="hover:text-gray-700">Today</Link>
        <span>/</span>
        <Link href="/subfields" className="hover:text-gray-700">Subfields</Link>
        <span>/</span>
        <Link href={`/subfields/${params.slug}`} className="hover:text-gray-700">{review.name}</Link>
        <span>/</span>
        <span className="text-gray-600">Literature review</span>
      </nav>

      {/* Header */}
      <div className="mb-8 pb-6 border-b border-gray-200">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-sans font-semibold text-purple-600 uppercase tracking-widest mb-2">Living Literature Review</p>
            <h1 className="headline-serif text-3xl sm:text-4xl text-gray-900 mb-2">{review.name}</h1>
            <div className="flex flex-wrap gap-4 text-xs font-sans text-gray-500">
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 inline-block" />
                Auto-updated daily at 02:00 UTC
              </span>
              {review.paper_count > 0 && <span>{review.paper_count} papers integrated</span>}
              {lastUpdated && <span>Last updated: {lastUpdated}</span>}
              {!review.is_seeded && (
                <span className="text-amber-600 font-medium">
                  ⚠ Historical foundation not yet seeded — run seed_literature.py
                </span>
              )}
            </div>
          </div>
          <Link
            href={`/subfields/${params.slug}`}
            className="text-sm font-sans font-medium text-blue-700 border border-blue-200 bg-blue-50 px-4 py-2 rounded-lg hover:bg-blue-100 transition-colors shrink-0"
          >
            ← Recent papers
          </Link>
        </div>
      </div>

      {/* Content */}
      {review.content_markdown ? (
        <LitReviewRenderer content={review.content_markdown} />
      ) : (
        <div className="text-center py-20">
          <div className="text-5xl mb-4">📖</div>
          <h2 className="headline-serif text-2xl text-gray-700 mb-2">Review not yet generated</h2>
          <p className="text-sm font-sans text-gray-500 max-w-md mx-auto">
            Run the seed script to generate the historical literature review for this subfield:
          </p>
          <code className="block mt-3 bg-gray-100 text-gray-700 text-xs font-mono px-4 py-2 rounded-lg inline-block">
            python scripts/seed_literature.py --subfield {params.slug}
          </code>
        </div>
      )}
    </div>
  );
}
