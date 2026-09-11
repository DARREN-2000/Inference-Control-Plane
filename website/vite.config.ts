import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: "/", // Updated for Render root deployment
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
