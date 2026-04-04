import { type ClassValue, clsx } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function formatDateShort(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export const FIELD_COLORS: Record<string, string> = {
  "fusion plasma":           "bg-rose-100 text-rose-800",
  "space plasma":            "bg-blue-100 text-blue-800",
  "astrophysical plasma":    "bg-purple-100 text-purple-800",
  "fundamental plasma physics": "bg-teal-100 text-teal-800",
  "laboratory plasma":       "bg-amber-100 text-amber-800",
  "high-energy-density plasma": "bg-orange-100 text-orange-800",
};

export const DEPTH_COLORS: Record<string, string> = {
  introductory:       "bg-green-100 text-green-800",
  intermediate:       "bg-blue-100 text-blue-800",
  advanced:           "bg-amber-100 text-amber-800",
  "highly specialized": "bg-red-100 text-red-800",
};

export const URGENCY_COLORS: Record<string, string> = {
  high:   "bg-red-100 text-red-800",
  medium: "bg-amber-100 text-amber-800",
  low:    "bg-green-100 text-green-800",
};

export function importanceColor(score: number): string {
  if (score >= 8) return "text-red-600";
  if (score >= 6) return "text-amber-600";
  if (score >= 4) return "text-blue-600";
  return "text-gray-500";
}

export function importanceBg(score: number): string {
  if (score >= 8) return "bg-red-500";
  if (score >= 6) return "bg-amber-500";
  if (score >= 4) return "bg-blue-500";
  return "bg-gray-300";
}
