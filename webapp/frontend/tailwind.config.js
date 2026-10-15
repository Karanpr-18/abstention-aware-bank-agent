/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        paper: '#F5F0E4',
        parchment: '#EFE7D3',
        ink: '#1A2420',
        green: '#0C2B23',
        greendeep: '#08211B',
        brass: '#A8842F',
        brasslight: '#D3B45E',
      },
      fontFamily: {
        serif: ['"Cormorant Garamond"', 'Georgia', 'serif'],
        sans: ['Inter', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
