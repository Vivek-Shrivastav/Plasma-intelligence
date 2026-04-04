import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ["var(--font-serif)", "Georgia", "serif"],
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      colors: {
        plasma: {
          50:  "#eef2ff",
          100: "#c7d4fa",
          200: "#a0b5f5",
          400: "#5a7de8",
          600: "#2d4fc5",
          800: "#1a2f85",
          900: "#0e1a4e",
        },
        accent: {
          50:  "#fef3e2",
          100: "#fddba0",
          400: "#f59e0b",
          600: "#b45309",
        },
      },
      typography: {
        DEFAULT: {
          css: {
            fontFamily: "var(--font-serif)",
            lineHeight: "1.85",
            "h1, h2, h3, h4": { fontFamily: "var(--font-serif)" },
          },
        },
      },
    },
  },
  plugins: [],
};

export default config;
