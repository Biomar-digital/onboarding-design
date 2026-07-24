/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Official BioMar brand palette (extracted from the brand deck theme)
        biomar: {
          navy: "#1F3E77", // BioMar deep blue (dk2 / accent1)
          blue: "#16356E", // deeper navy for gradients / hover
          swoosh: "#0471AD", // BioMar bright blue (swoosh accent)
          sky: "#92CEE8", // light swoosh blue
          ice: "#EAF4FB", // pale background tint
          pale: "#C3E4EF", // brand pale blue
          green: "#97D130", // brand green accent
          sand: "#EAB318", // brand yellow accent
          orange: "#DD6928", // brand orange accent
          gray: "#575756", // brand warm gray (dk1)
        },
      },
      fontFamily: {
        sans: ["Inter", "Segoe UI", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(10,42,84,0.06), 0 8px 24px rgba(10,42,84,0.08)",
      },
    },
  },
  plugins: [],
};
