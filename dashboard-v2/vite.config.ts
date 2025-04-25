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
        test: resolve(__dirname, 'public/test.html'),
        diagnostic: resolve(__dirname, 'diagnostic.html')
      }
    }
  }
})
