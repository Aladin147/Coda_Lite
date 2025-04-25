/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4d9aff',
          light: '#6fb1ff',
          dark: '#3a86ff',
        },
        secondary: {
          DEFAULT: '#9d5cff',
          light: '#b57dff',
          dark: '#8338ec',
        },
        success: {
          DEFAULT: '#10e3b0',
          light: '#3aeac1',
          dark: '#06d6a0',
        },
        warning: {
          DEFAULT: '#ffc72c',
          light: '#ffd45e',
          dark: '#ffbe0b',
        },
        danger: {
          DEFAULT: '#ff5c7c',
          light: '#ff7d96',
          dark: '#ef476f',
        },
        background: {
          DEFAULT: '#121212',
          card: '#1e1e1e',
          light: '#f8f9fa',
        },
        text: {
          DEFAULT: '#e9ecef',
          secondary: '#adb5bd',
          dark: '#212529',
        },
        border: {
          DEFAULT: '#2d2d2d',
          light: '#dee2e6',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'breathe': 'breathe 4s ease-in-out infinite',
        'wave': 'wave 1.5s ease-in-out infinite',
      },
      keyframes: {
        breathe: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' },
        },
        wave: {
          '0%': { transform: 'scaleY(0.5)' },
          '50%': { transform: 'scaleY(1)' },
          '100%': { transform: 'scaleY(0.5)' },
        },
      },
    },
  },
  plugins: [],
}
