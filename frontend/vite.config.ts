// 作用：配置 Vite React 插件、本地开发服务器，以及后端 API 反向代理以规避跨域。

import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const backend = env.VITE_BACKEND_ORIGIN || 'http://127.0.0.1:8000';

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        '/chat': {
          target: backend,
          changeOrigin: true,
          ws: false,
        },
        '/api': {
          target: backend,
          changeOrigin: true,
        },
      },
    },
  };
});

