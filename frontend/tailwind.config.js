/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Turkish çini-tile inspired palette — deliberately not the
        // warm-cream+terracotta or near-black+neon defaults.
        stone: {
          50: '#F7F6F2',
          100: '#EDEEEA', // page background — pale stone, cool not warm-cream
          200: '#E0E1DA',
        },
        ink: '#241F19', // near-black umber, not pure black
        teal: {
          DEFAULT: '#1F6F78', // primary accent — çini tile teal
          dark: '#164F56',
          light: '#DCEBEC',
        },
        gold: {
          DEFAULT: '#D6A21B', // secondary accent — score highlight
          light: '#F6E8C2',
        },
        brick: {
          DEFAULT: '#B4432E', // reserved for alerts/low scores only
          light: '#F3DCD6',
        },
        charcoal: '#23211D', // admin sidebar / dark surfaces
      },
      fontFamily: {
        display: ['"Fraunces"', 'serif'],
        body: ['"IBM Plex Sans"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
