/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
    "./static/**/*.html",
    "../templates/**/*.html",  // templates del proyecto Django
    "./**/*.html",
    "./**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
