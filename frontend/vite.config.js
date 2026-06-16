import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const API_TARGET = 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,
    open: false,
    proxy: {
      '/api': {
        target: API_TARGET,
        changeOrigin: true,
        timeout: 120000,
      },
      '/uploads': {
        target: API_TARGET,
        changeOrigin: true,
      },
    },
  },
})
