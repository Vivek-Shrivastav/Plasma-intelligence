"use client";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeHighlight from "rehype-highlight";
import { useEffect, useState } from "react";

interface Props {
  content: string;
  className?: string;
}

export default function LitReviewRenderer({ content, className }: Props) {
  const [toc, setToc] = useState<{ id: string; text: string; level: number }[]>([]);

  useEffect(() => {
    // Build table of contents from headings
    const headings: { id: string; text: string; level: number }[] = [];
    const lines = content.split("\n");
    lines.forEach(line => {
      const m2 = line.match(/^## (.+)/);
      const m3 = line.match(/^### (.+)/);
      if (m2) {
        const text = m2[1].trim();
        headings.push({ id: text.toLowerCase().replace(/[^a-z0-9]+/g, "-"), text, level: 2 });
      } else if (m3) {
        const text = m3[1].trim();
        headings.push({ id: text.toLowerCase().replace(/[^a-z0-9]+/g, "-"), text, level: 3 });
      }
    });
    setToc(headings);
  }, [content]);

  return (
    <div className="flex gap-8">
      {/* TOC Sidebar */}
      {toc.length > 0 && (
        <aside className="hidden lg:block w-52 shrink-0">
          <div className="sticky top-24 max-h-[80vh] overflow-y-auto">
            <p className="text-xs font-sans font-semibold text-gray-500 uppercase tracking-wider mb-3">Contents</p>
            <nav className="space-y-1">
              {toc.map((item) => (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  className={`block text-xs font-sans text-gray-600 hover:text-blue-700 transition-colors leading-snug py-0.5 ${
                    item.level === 3 ? "pl-3 text-gray-500" : "font-medium"
                  }`}
                >
                  {item.text.replace(/\*\*/g, "")}
                </a>
              ))}
            </nav>
          </div>
        </aside>
      )}

      {/* Main content */}
      <div className={`prose-plasma flex-1 min-w-0 ${className ?? ""}`}>
        <ReactMarkdown
          remarkPlugins={[remarkGfm, remarkMath]}
          rehypePlugins={[rehypeHighlight]}
          components={{
            h2: ({ children }) => {
              const text = String(children);
              const id = text.toLowerCase().replace(/[^a-z0-9]+/g, "-");
              return <h2 id={id}>{children}</h2>;
            },
            h3: ({ children }) => {
              const text = String(children);
              const id = text.toLowerCase().replace(/[^a-z0-9]+/g, "-");
              return <h3 id={id}>{children}</h3>;
            },
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
