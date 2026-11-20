import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    // 开发环境把 /api 代理到后端，浏览器同源，彻底绕开跨域问题
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      },
      // 上传的图片存在后端目录里，也要代理过去，
      // 否则 <img src="/uploads/xxx.jpg"> 会被 vite 当成本地静态资源，直接 404
      '/uploads': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})
