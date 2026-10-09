import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: false,
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/students': 'http://127.0.0.1:8000',
      '/cohort': 'http://127.0.0.1:8000',
      '/simulate': 'http://127.0.0.1:8000',
      '/intervention': 'http://127.0.0.1:8000',
      '/intervene': 'http://127.0.0.1:8000',
      '/scoring': 'http://127.0.0.1:8000',
      '/data': 'http://127.0.0.1:8000',
      '/timetable': 'http://127.0.0.1:8000',
      '/attendance': 'http://127.0.0.1:8000',
      '/marks': 'http://127.0.0.1:8000',
      '/assignments': 'http://127.0.0.1:8000',
      '/announcements': 'http://127.0.0.1:8000',
      '/examinations': 'http://127.0.0.1:8000',
      '/fees': 'http://127.0.0.1:8000',
      '/notifications': 'http://127.0.0.1:8000',
      '/admin': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
    }
  }
})
