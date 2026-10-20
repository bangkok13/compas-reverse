<script setup lang="ts">
const props = defineProps<{ items: { label: string; to?: string }[] }>()
const config = useRuntimeConfig()
const route = useRoute()
useStructuredData(() => ({
  '@context': 'https://schema.org', '@type': 'BreadcrumbList',
  itemListElement: [{ label: 'Главная', to: '/' }, ...props.items].map((item, index) => ({
    '@type': 'ListItem', position: index + 1, name: item.label,
    item: `${config.public.siteUrl}${item.to || route.path}`,
  })),
}))
</script>
<template><nav class="breadcrumbs" aria-label="Хлебные крошки"><NuxtLink to="/">Главная</NuxtLink><template v-for="(item, i) in items" :key="i"><span aria-hidden="true">/</span><NuxtLink v-if="item.to" :to="item.to">{{ item.label }}</NuxtLink><span v-else aria-current="page">{{ item.label }}</span></template></nav></template>
