import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },
  ssr: true,
  css: ['@fontsource-variable/manrope', '~/assets/css/main.css'],
  vite: { plugins: [tailwindcss()] },
  runtimeConfig: {
    apiInternal: 'http://127.0.0.1:8000/api',
    public: { siteUrl: 'http://localhost:8080', indexable: false },
  },
  app: {
    head: {
      htmlAttrs: { lang: 'ru' },
      meta: [{ name: 'theme-color', content: '#11151c' }],
      link: [{ rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    },
  },
  typescript: { strict: true },
  routeRules: {
    '/api/**': { headers: { 'cache-control': 'no-store' } },
  },
})
