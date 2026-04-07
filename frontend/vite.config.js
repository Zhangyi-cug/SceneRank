import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/projects/SceneRank/survey/',
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
