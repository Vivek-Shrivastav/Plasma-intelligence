"use client";
import Link from "next/link";
import Image from "next/image";
import { cn, formatDateShort, FIELD_COLORS, DEPTH_COLORS, importanceColor, importanceBg } from "@/lib/utils";
import type { Paper } from "@/lib/api";

interface Props {
  paper: Paper;
  variant?: "headline" | "card" | "compact";
}

export default function PaperCard({ paper, variant = "card" }: Props) {
  const score = paper.importance_score ?? 0;
  const fieldColor = FIELD_COLORS[paper.field ?? ""] ?? "bg-gray-100 text-gray-700";
  const depthColor = DEPTH_COLORS[paper.technical_depth ?? ""] ?? "bg-gray-100 text-gray-700";
  const firstFigure = paper.figures?.[0];

  if (variant === "compact") {
    return (
      <Link href={`/paper/${paper.id}`} className="group block py-3 border-b border-gray-100 hover:bg-gray-50 transition-colors px-1">
        <div className="flex gap-3 items-start">
          <span className={cn("text-sm font-bold font-sans mt-0.5 w-5 text-right shrink-0", importanceColor(score))}>
            {score}
          </span>
          <div className="min-w-0">
            <p className="headline-serif text-sm leading-snug text-gray-900 group-hover:text-blue-800 transition-colors line-clamp-2">
              {paper.headline ?? paper.title}
            </p>
            <p className="text-xs text-gray-500 font-sans mt-1">
              {paper.authors?.[0]?.split(",")[0]} et al. · {paper.journal} · {formatDateShort(paper.published_date)}
            </p>
          </div>
          {firstFigure && (
            <div className="shrink-0 w-12 h-10 rounded overflow-hidden bg-gray-100 relative">
              <Image src={firstFigure.url} alt="figure" fill className="object-cover" />
            </div>
          )}
        </div>
      </Link>
    );
  }

  if (variant === "headline") {
    return (
      <Link href={`/paper/${paper.id}`} className="group block">
        {firstFigure && (
          <div className="relative w-full h-44 rounded-lg overflow-hidden bg-gray-100 mb-3">
            <Image src={firstFigure.url} alt={firstFigure.description} fill className="object-cover" />
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-2">
              <p className="text-white text-xs font-sans opacity-90 line-clamp-1">{firstFigure.description}</p>
            </div>
          </div>
        )}
        <div className="flex gap-2 items-center mb-1.5 flex-wrap">
          {paper.field && <span className={cn("text-xs font-sans font-medium px-2 py-0.5 rounded-full", fieldColor)}>{paper.field}</span>}
          <span className={cn("text-xs font-sans font-medium", importanceColor(score))}>Score {score}/10</span>
        </div>
        <h2 className="headline-serif text-xl leading-tight text-gray-900 group-hover:text-blue-800 transition-colors mb-2">
          {paper.headline ?? paper.title}
        </h2>
        <p className="text-sm text-gray-600 font-sans leading-relaxed line-clamp-3">{paper.short_summary}</p>
        <p className="text-xs text-gray-400 font-sans mt-2">
          {paper.authors?.slice(0, 2).map(a => a.split(",")[0]).join(", ")}{paper.authors?.length > 2 ? " et al." : ""} · {paper.journal}
        </p>
      </Link>
    );
  }

  // default: card
  return (
    <Link href={`/paper/${paper.id}`} className="group block bg-white border border-gray-200 rounded-xl p-4 hover:border-blue-300 hover:shadow-sm transition-all">
      <div className="flex gap-4 items-start">
        {firstFigure && (
          <div className="shrink-0 relative w-20 h-16 rounded-lg overflow-hidden bg-gray-100">
            <Image src={firstFigure.url} alt="figure" fill className="object-cover" />
          </div>
        )}
        <div className="min-w-0 flex-1">
          {/* importance bar */}
          <div className="flex items-center gap-2 mb-1.5">
            <div className="importance-bar w-16">
              <div className={cn("h-full rounded-full transition-all", importanceBg(score))} style={{ width: `${score * 10}%` }} />
            </div>
            <span className={cn("text-xs font-sans font-semibold", importanceColor(score))}>{score}/10</span>
            {paper.field && <span className={cn("text-xs font-sans px-2 py-0.5 rounded-full", fieldColor)}>{paper.field}</span>}
            {paper.technical_depth && <span className={cn("text-xs font-sans px-2 py-0.5 rounded-full", depthColor)}>{paper.technical_depth}</span>}
          </div>
          <h3 className="headline-serif text-base leading-snug text-gray-900 group-hover:text-blue-800 transition-colors mb-1 line-clamp-2">
            {paper.headline ?? paper.title}
          </h3>
          <p className="text-xs text-gray-500 font-sans line-clamp-2 leading-relaxed">{paper.short_summary}</p>
          <div className="flex flex-wrap gap-2 mt-2 items-center">
            <span className="text-xs text-gray-400 font-sans">
              {paper.authors?.[0]?.split(",")[0]}{paper.authors?.length > 1 ? " et al." : ""} · {paper.journal} · {formatDateShort(paper.published_date)}
            </span>
            {paper.subfields?.slice(0, 2).map(s => (
              <span key={s} className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-sans">{s}</span>
            ))}
          </div>
        </div>
      </div>
    </Link>
  );
}
