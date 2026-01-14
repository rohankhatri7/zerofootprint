import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["IBM Plex Sans", "sans-serif"]
      },
      colors: {
        ink: "#0b1b1f",
        sand: "#f6f0e8",
        clay: "#f0dfc7",
        rust: "#cc5b2d",
        mint: "#8ad4c8",
        sea: "#1c6b7a"
      }
    }
  },
  plugins: []
} satisfies Config;
