/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // BioMar brand palette
        biomar: {
          navy: "#0A2A54", // deep corporate navy
          blue: "#123E7C",
          swoosh: "#00A0DC", // bright swoosh cyan-blue
          sky: "#CFE8F5",
          ice: "#EAF4FB",
          green: "#7AB648", // EWOS / change quadrant accent
          sand: "#F5A623",
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
