export default defineEventHandler(event => {
  const config = useRuntimeConfig(event)
  const url = getRequestURL(event)
  return proxyRequest(event, `${String(config.apiInternal).replace(/\/api\/?$/, '')}${url.pathname}`)
})
