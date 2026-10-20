export default defineEventHandler(event => {
  const config = useRuntimeConfig(event)
  setHeader(event, 'content-type', 'text/plain; charset=utf-8')
  const enabled = config.public.indexable === true || String(config.public.indexable) === 'true'
  return enabled
    ? `User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/\nDisallow: /privacy\nDisallow: /consent\nSitemap: ${config.public.siteUrl}/sitemap.xml\n`
    : 'User-agent: *\nDisallow: /\n'
})
