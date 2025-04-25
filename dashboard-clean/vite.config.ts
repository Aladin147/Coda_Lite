import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        minimal: resolve(__dirname, 'minimal.html'),
        minimalTest: resolve(__dirname, 'minimal-test.html'),
        minimalDashboard: resolve(__dirname, 'minimal-dashboard.html')
      }
    }
  }
})
