import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/v1': {
        target: 'https://stock.asvig.com',
        changeOrigin: true,
        secure: false,
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes) => {
            const location = proxyRes.headers['location'];
            if (location && proxyRes.statusCode && proxyRes.statusCode >= 300 && proxyRes.statusCode < 400) {
              try {
                const url = new URL(location);
                proxyRes.headers['location'] = url.pathname + url.search;
              } catch {}
            }
          });
        },
      },
    },
  },
})
