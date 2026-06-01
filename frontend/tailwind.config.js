/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        space: {
          950: '#04040f',
          900: '#080820',
          800: '#0d0d2b',
          700: '#111136',
          600: '#1a1a4e',
        },
        nebula: {
          purple: '#7c3aed',
          blue: '#2563eb',
          teal: '#0d9488',
          pink: '#db2777',
        },
      },
      backgroundImage: {
        'space-gradient': 'linear-gradient(to bottom, #04040f 0%, #0d0d2b 50%, #080820 100%)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'twinkle': 'twinkle 3s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        twinkle: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.2 },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
    },
  },
  plugins: [],
}
