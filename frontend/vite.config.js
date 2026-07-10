import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  // En producción (Render) el build va dentro de Flask/static/dist
  // para que Flask lo sirva directamente.
  build: {
    outDir: '../backend/app/static/dist',
    emptyOutDir: true,
  },
  server: {
    port: 5173
  }
})
