/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },
        lavender: {
          50: '#faf8ff',
          100: '#f4f1fd',
          200: '#e9e3fb',
          300: '#d9cdfa',
          400: '#c0abf6',
          500: '#a582f0',
          600: '#8c59e7',
          700: '#7940d5',
          800: '#6435b3',
          900: '#532d92',
        },
        surface: {
          light: '#f6f5fb',
          panel: '#ffffff',
          dark: '#0d111d',
          darkpanel: '#151b2b',
          darkborder: '#232d45',
        },
        risk: {
          high: '#ef4444',
          medium: '#f59e0b',
          low: '#10b981',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'subtle': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)',
        'card': '0 4px 20px -2px rgba(99, 102, 241, 0.06), 0 2px 6px -1px rgba(0, 0, 0, 0.04)',
        'card-dark': '0 4px 20px -2px rgba(0, 0, 0, 0.4), 0 2px 6px -1px rgba(0, 0, 0, 0.3)',
      }
    },
  },
  plugins: [],
}
