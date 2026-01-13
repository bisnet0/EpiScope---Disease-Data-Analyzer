import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // --- CONFIGURAÇÃO DO PROXY ---
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // O Vite vai jogar tudo pro Python aqui
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '') // Remove o '/api' antes de mandar pro back
      }
    }
  }
})