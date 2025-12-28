import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    middlewareMode: true,
  },
  build: {
    outDir: 'dist',
    // NOTE: enabled temporarily to debug production errors — revert after we capture stacks
    sourcemap: true,
    minify: false,
  },
})