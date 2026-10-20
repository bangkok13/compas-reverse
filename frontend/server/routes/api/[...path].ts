export default defineEventHandler(event => {
  const config = useRuntimeConfig(event)
  const url = getRequestURL(event)
  const target = `${config.apiInternal}${url.pathname.slice(4)}${url.search}`
  // Local development proxy. In Docker, Nginx routes /api directly to Django.
  return proxyRequest(event, target, {
    headers: {
      host: getHeader(event, 'host') || 'localhost',
      'x-real-ip': getRequestIP(event) || '127.0.0.1',
      'x-forwarded-proto': url.protocol.replace(':', ''),
    },
  })
})
