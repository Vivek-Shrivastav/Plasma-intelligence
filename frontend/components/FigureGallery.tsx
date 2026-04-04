"use client";
import { useState } from "react";
import Image from "next/image";
import type { Figure } from "@/lib/api";

export default function FigureGallery({ figures }: { figures: Figure[] }) {
  const [selected, setSelected] = useState<number | null>(null);

  if (!figures || figures.length === 0) return null;

  return (
    <div>
      {/* Thumbnail grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 mt-4">
        {figures.map((fig, i) => (
          <button
            key={i}
            onClick={() => setSelected(i)}
            className="group relative aspect-[4/3] rounded-lg overflow-hidden bg-gray-100 border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all"
          >
            <Image src={fig.url} alt={fig.description || `Figure ${i + 1}`} fill className="object-cover group-hover:scale-105 transition-transform duration-300" />
            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />
            <span className="absolute bottom-1 right-1 bg-black/60 text-white text-xs px-1.5 py-0.5 rounded font-sans">
              Fig. {i + 1}
            </span>
          </button>
        ))}
      </div>

      {/* Lightbox */}
      {selected !== null && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
          onClick={() => setSelected(null)}
        >
          <div
            className="bg-white rounded-2xl overflow-hidden max-w-4xl w-full max-h-[90vh] flex flex-col"
            onClick={e => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-3 border-b border-gray-200">
              <div className="flex gap-2">
                {figures.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setSelected(i)}
                    className={`w-2 h-2 rounded-full transition-colors ${i === selected ? "bg-gray-900" : "bg-gray-300 hover:bg-gray-500"}`}
                  />
                ))}
              </div>
              <span className="text-xs text-gray-500 font-sans">Figure {selected + 1} of {figures.length}</span>
              <button onClick={() => setSelected(null)} className="text-gray-400 hover:text-gray-700 text-xl leading-none font-sans">×</button>
            </div>

            {/* Figure */}
            <div className="relative flex-1 min-h-0 bg-gray-50" style={{ minHeight: "300px", maxHeight: "60vh" }}>
              <Image
                src={figures[selected].url}
                alt={figures[selected].description}
                fill
                className="object-contain p-2"
              />
            </div>

            {/* Description */}
            {figures[selected].description && (
              <div className="px-5 py-4 border-t border-gray-200 bg-gray-50">
                <p className="text-sm text-gray-700 font-sans leading-relaxed">
                  <span className="font-semibold text-gray-900">Fig. {selected + 1}: </span>
                  {figures[selected].description}
                </p>
              </div>
            )}

            {/* Navigation */}
            <div className="flex justify-between px-4 pb-4 pt-2">
              <button
                disabled={selected === 0}
                onClick={() => setSelected(s => (s ?? 0) - 1)}
                className="px-4 py-1.5 text-sm font-sans rounded-lg border border-gray-200 hover:bg-gray-100 disabled:opacity-30 transition-colors"
              >
                ← Previous
              </button>
              <button
                disabled={selected === figures.length - 1}
                onClick={() => setSelected(s => (s ?? 0) + 1)}
                className="px-4 py-1.5 text-sm font-sans rounded-lg border border-gray-200 hover:bg-gray-100 disabled:opacity-30 transition-colors"
              >
                Next →
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
