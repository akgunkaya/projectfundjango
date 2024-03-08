/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './taskapp/templates/**/*.html',
    './node_modules/flowbite/**/*.js'    
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('flowbite/plugin')
  ],
  darkMode: 'class',
}

