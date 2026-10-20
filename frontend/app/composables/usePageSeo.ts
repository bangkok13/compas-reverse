export function usePageSeo(title: () => string, description: () => string, image?: () => string) {
  const route = useRoute()
  const config = useRuntimeConfig()
  const origin = String(config.public.siteUrl).replace(/\/$/, '')
  const canonical = computed(() => `${origin}${route.path}`)
  useSeoMeta({
    title,
    description,
    ogTitle: title,
    ogDescription: description,
    ogType: 'website',
    ogLocale: 'ru_RU',
    ogUrl: canonical,
    ogImage: () => {
      const src = image?.() || '/og-image.png'
      return src.startsWith('http') ? src : `${origin}${src}`
    },
    twitterCard: 'summary_large_image',
    robots: () => config.public.indexable === true || String(config.public.indexable) === 'true'
      ? 'index, follow' : 'noindex, nofollow',
  })
  useHead({ link: [{ rel: 'canonical', href: canonical }] })
}

export function useStructuredData(data: () => Record<string, unknown>) {
  useHead(() => ({
    script: [{ type: 'application/ld+json', innerHTML: JSON.stringify(data()).replace(/</g, '\\u003c') }],
  }))
}
