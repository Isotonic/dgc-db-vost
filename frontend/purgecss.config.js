// purgecss config - https://www.purgecss.com/configuration
module.exports = {
  content: [
    './dist/**/*.html',
    './dist/js/*.js'
  ],
  css: [
    './dist/css/*.css'
  ],
  whitelistPatterns: [
    /^router-link(|-exact)-active$/
  ]
}
