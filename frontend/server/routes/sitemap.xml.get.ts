type Row = { slug: string }
type Page = { results: Row[]; next: string | null }
export default defineEventHandler(async event => {
  const config = useRuntimeConfig(event)
  const base = String(config.apiInternal)
  const [services, materials] = await Promise.all([
    $fetch<Row[]>(`${base}/services/`), $fetch<Row[]>(`${base}/materials/`),
  ])
  const projects: Row[] = []
  let page = 1
  while (true) {
    const result = await $fetch<Page>(`${base}/projects/`, { query: { page } })
    projects.push(...result.results)
    if (!result.next) break
    page++
  }
  const paths = ['/', '/services', '/projects', '/materials', '/contacts',
    ...services.map(s => `/services/${s.slug}`),
    ...materials.map(m => `/materials/${m.slug}`),
    ...projects.map(p => `/projects/${p.slug}`),
  ]
  const escape = (s: string) => s.replace(/[<>&"']/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;' })[c]!)
  setHeader(event, 'content-type', 'application/xml; charset=utf-8')
  return `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${paths.map(path => `<url><loc>${escape(`${config.public.siteUrl}${path}`)}</loc></url>`).join('')}</urlset>`
})
