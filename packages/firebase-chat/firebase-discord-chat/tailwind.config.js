/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        discord: {
          dark: '#36393f',
          darker: '#2f3136',
          darkest: '#202225',
          blurple: '#5865f2',
          green: '#3ba55d',
          yellow: '#faa81a',
          red: '#ed4245',
          gray: {
            100: '#dcddde',
            200: '#b9bbbe',
            300: '#8e9297',
            400: '#72767d',
            500: '#4f545c',
          }
        }
      },
      fontFamily: {
        sans: [
          'Whitney', 
          '-apple-system', 
          'BlinkMacSystemFont', 
          'Segoe UI', 
          'Roboto', 
          'Helvetica', 
          'Arial', 
          'sans-serif'
        ],
      },
      spacing: {
        '18': '4.5rem',
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
      }
    },
  },
  plugins: [],
} 