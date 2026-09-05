/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        walnut: {
          50: '#F7F4F0',
          100: '#EFE7DE',
          200: '#D9C8B5',
          300: '#C2A88C',
          400: '#8E6749',
          500: '#5C3D2E', // Primary Deep Walnut Brown
          600: '#4D3326',
          700: '#3D281E',
          800: '#2E1E17',
          850: '#261912',
          900: '#1E140F',
          950: '#140D0A',
        },
        cream: {
          50: '#FFFFFF',
          100: '#FAF7F4', // Background Off-White
          200: '#F5EFE6', // Secondary Warm Cream / Linen
          300: '#E6D9C8',
          400: '#D6C3AA',
        },
        gold: {
          400: '#E0B058',
          500: '#C9963F', // Accent Burnished Gold
          600: '#A6792B',
        },
        charcoal: '#1E1E1E', // Text Primary
        softgray: '#6B6B6B', // Text Secondary
        mutedgreen: '#4CAF76', // Success
        dustyrose: '#D9534F', // Error
      },
      fontFamily: {
        serif: ['"Playfair Display"', 'serif'],
        sans: ['"Inter"', 'sans-serif'],
      },
      boxShadow: {
        'warm': '0 4px 20px -2px rgba(92, 61, 46, 0.08)',
        'warm-lg': '0 10px 25px -3px rgba(92, 61, 46, 0.12)',
        'card': '0 2px 12px rgba(30, 30, 30, 0.04)',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      }
    },
  },
  plugins: [],
}
