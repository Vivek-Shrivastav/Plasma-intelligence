"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const links = [
  { href: "/",               label: "Today" },
  { href: "/subfields",      label: "Subfields" },
  { href: "/open-problems",  label: "Open Problems" },
];

export default function Nav() {
  const path = usePathname();
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        {/* Masthead */}
        <div className="masthead-rule my-0" />
        <div className="flex items-center justify-between py-3">
          <Link href="/" className="headline-serif text-xl tracking-tight text-gray-900">
            ⚛ Plasma Intelligence
          </Link>
          <nav className="flex gap-1">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className={cn(
                  "px-3 py-1.5 rounded text-sm font-sans font-medium transition-colors",
                  path === l.href
                    ? "bg-gray-900 text-white"
                    : "text-gray-600 hover:bg-gray-100"
                )}
              >
                {l.label}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}
