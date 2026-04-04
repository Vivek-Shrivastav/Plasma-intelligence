import { api } from "@/lib/api";
import Link from "next/link";

export const revalidate = 3600;

const SUBFIELD_DESCRIPTIONS: Record<string, string> = {
  "magnetic-reconnection": "Explosive topology changes in magnetized plasma driving energy release",
  "plasma-turbulence": "Nonlinear wave interactions and anomalous transport in turbulent plasmas",
  "two-stream-instability": "Kinetic instability when counter-streaming beams drive electrostatic waves",
  "tokamak": "Toroidal magnetic confinement devices for controlled fusion research",
  "stellarator": "Twisted magnetic confinement geometry with no net toroidal current",
  "solar-wind": "Supersonic magnetized plasma flow from the Sun through the heliosphere",
  "magnetosphere": "Earth's and planetary magnetic environments shaped by the solar wind",
  "mhd-waves": "Alfvén, magnetosonic, and whistler waves in magnetized plasmas",
  "kinetic-effects": "Non-fluid, particle-level dynamics beyond the MHD approximation",
  "plasma-heating": "RF, NBI, ohmic and laser-based energy deposition in plasma",
  "confinement": "Magnetic and inertial strategies for holding hot plasma together",
  "transport": "Anomalous particle and energy fluxes driven by instabilities and turbulence",
  "shocks": "Collisionless shock waves in space and laboratory plasmas",
  "accretion-disks": "Magnetized plasma dynamics around compact astrophysical objects",
  "pic-simulations": "First-principles particle-in-cell kinetic plasma modeling",
  "drift-waves": "Cross-field density gradient driven waves governing tokamak edge transport",
  "plasma-instability": "Linear and nonlinear growth of perturbations in magnetized plasma",
  "diagnostics": "Experimental measurement techniques for plasma parameters",
};

const SUBFIELD_ICONS: Record<string, string> = {
  "magnetic-reconnection": "⚡",
  "plasma-turbulence": "🌀",
  "two-stream-instability": "↔",
  "tokamak": "○",
  "stellarator": "∿",
  "solar-wind": "☀",
  "magnetosphere": "🌍",
  "mhd-waves": "〜",
  "kinetic-effects": "·",
  "plasma-heating": "▲",
  "confinement": "◎",
  "transport": "→",
  "shocks": "»",
  "accretion-disks": "◉",
  "pic-simulations": "⊞",
  "drift-waves": "≋",
  "plasma-instability": "↑",
  "diagnostics": "⊡",
};

export default async function SubfieldsPage() {
  let subfields;
  try {
    subfields = await api.subfields.list();
  } catch {
    subfields = [];
  }

  const groups: Record<string, typeof subfields> = {
    "Fusion & Confinement": subfields.filter(s =>
      ["tokamak", "stellarator", "confinement", "plasma-heating", "transport", "diagnostics"].includes(s.slug)
    ),
    "Instabilities & Waves": subfields.filter(s =>
      ["plasma-instability", "two-stream-instability", "drift-waves", "mhd-waves", "plasma-turbulence"].includes(s.slug)
    ),
    "Space & Astrophysical": subfields.filter(s =>
      ["solar-wind", "magnetosphere", "shocks", "accretion-disks", "magnetic-reconnection"].includes(s.slug)
    ),
    "Kinetics & Simulation": subfields.filter(s =>
      ["kinetic-effects", "pic-simulations"].includes(s.slug)
    ),
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 fade-in">
      <div className="mb-8">
        <h1 className="headline-serif text-4xl text-gray-900 mb-2">Subfields</h1>
        <p className="text-gray-500 font-sans text-sm max-w-xl">
          Browse papers by subfield. Each section shows the last 6 months of publications with full analyses, figures, and a living literature review.
        </p>
      </div>

      {Object.entries(groups).map(([groupName, items]) => (
        items.length > 0 && (
          <div key={groupName} className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <h2 className="headline-serif text-lg text-gray-700">{groupName}</h2>
              <div className="h-px bg-gray-200 flex-1" />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {items.map(sf => (
                <Link key={sf.slug} href={`/subfields/${sf.slug}`}
                  className="group bg-white border border-gray-200 rounded-xl p-5 hover:border-blue-300 hover:shadow-sm transition-all">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl shrink-0 mt-0.5">{SUBFIELD_ICONS[sf.slug] ?? "·"}</span>
                    <div>
                      <h3 className="headline-serif text-base text-gray-900 group-hover:text-blue-800 transition-colors mb-1">
                        {sf.name}
                      </h3>
                      <p className="text-xs font-sans text-gray-500 leading-relaxed">
                        {SUBFIELD_DESCRIPTIONS[sf.slug] ?? ""}
                      </p>
                    </div>
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-100 flex gap-3">
                    <span className="text-xs font-sans text-blue-600 group-hover:underline">Papers →</span>
                    <span className="text-xs font-sans text-gray-400">|</span>
                    <Link href={`/subfields/${sf.slug}/literature`}
                      className="text-xs font-sans text-purple-600 hover:underline"
                      onClick={e => e.stopPropagation()}>
                      Literature review →
                    </Link>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )
      ))}
    </div>
  );
}
