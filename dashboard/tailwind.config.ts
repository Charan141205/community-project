import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#090d16",
        surface: "#111827",
        "surface-elevated": "#1f2937",
        border: "#374151",
        primary: {
          50: "#eff6ff",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
        risk: {
          normal: "#10b981",    // Green
          watch: "#f59e0b",     // Amber / Yellow
          warning: "#f97316",   // Orange
          critical: "#ef4444",  // Red
          offline: "#6b7280",   // Grey
        },
      },
      animation: {
        "pulse-critical": "pulse-critical 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow-route": "glow-route 2s ease-in-out infinite",
      },
      keyframes: {
        "pulse-critical": {
          "0%, 100%": { opacity: "1", transform: "scale(1)" },
          "50%": { opacity: "0.6", transform: "scale(1.15)" },
        },
        "glow-route": {
          "0%, 100%": { strokeDashoffset: "0" },
          "50%": { strokeDashoffset: "20" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
