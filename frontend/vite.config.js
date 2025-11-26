import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: process.env.NODE_ENV === 'development' ? {
      '/api': {
        target: 'http://localhost:8002',
        changeOrigin: true,
      },
    } : undefined,
  },
})

