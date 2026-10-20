import type { SiteSettings } from '~/types'

export function useApi<T>(path: string | (() => string), options: { query?: MaybeRef<Record<string, unknown>> } = {}) {
  const config = useRuntimeConfig()
  const key = computed(() => `api:${toValue(path)}:${JSON.stringify(toValue(options.query) || {})}`)
  return useAsyncData<T>(key, () => $fetch<T>(toValue(path), {
    baseURL: import.meta.server ? String(config.apiInternal) : '/api',
    query: toValue(options.query),
  }) as Promise<T>)
}

export function useSiteSettings() {
  return useState<SiteSettings | null>('site-settings', () => null)
}
