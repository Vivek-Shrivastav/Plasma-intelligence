"use client";
import { cn, importanceColor, importanceBg } from "@/lib/utils";

export function ImportanceBar({ score }: { score: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="importance-bar w-24 h-1.5">
        <div
          className={cn("h-full rounded-full", importanceBg(score))}
          style={{ width: `${score * 10}%` }}
        />
      </div>
      <span className={cn("text-sm font-sans font-semibold tabular-nums", importanceColor(score))}>
        {score}<span className="text-gray-400 font-normal">/10</span>
      </span>
    </div>
  );
}

export function FieldBadge({ field }: { field: string }) {
  const colors: Record<string, string> = {
    "fusion plasma": "bg-rose-50 text-rose-700 border-rose-200",
    "space plasma": "bg-sky-50 text-sky-700 border-sky-200",
    "astrophysical plasma": "bg-violet-50 text-violet-700 border-violet-200",
    "fundamental plasma physics": "bg-teal-50 text-teal-700 border-teal-200",
    "laboratory plasma": "bg-amber-50 text-amber-700 border-amber-200",
    "high-energy-density plasma": "bg-orange-50 text-orange-700 border-orange-200",
  };
  const cls = colors[field] ?? "bg-gray-50 text-gray-700 border-gray-200";
  return (
    <span className={cn("inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-sans font-medium border", cls)}>
      {field}
    </span>
  );
}

export function SubfieldPill({ name }: { name: string }) {
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-sans bg-slate-100 text-slate-700 border border-slate-200">
      {name}
    </span>
  );
}

export function ConceptPill({ name }: { name: string }) {
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-sans bg-indigo-50 text-indigo-700 border border-indigo-200">
      {name}
    </span>
  );
}

export function DepthBadge({ depth }: { depth: string }) {
  const colors: Record<string, string> = {
    introductory: "bg-green-50 text-green-700 border-green-200",
    intermediate: "bg-blue-50 text-blue-700 border-blue-200",
    advanced: "bg-amber-50 text-amber-700 border-amber-200",
    "highly specialized": "bg-red-50 text-red-700 border-red-200",
  };
  const cls = colors[depth] ?? "bg-gray-50 text-gray-600 border-gray-200";
  return (
    <span className={cn("inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-sans font-medium border", cls)}>
      {depth}
    </span>
  );
}
