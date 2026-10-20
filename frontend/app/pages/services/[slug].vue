<script setup lang="ts">
import type { Service, Project, Paginated } from '~/types'
const route = useRoute()
const settings = useSiteSettings()
const config = useRuntimeConfig()
const { data: service, error } = await useApi<Service>(`/services/${route.params.slug}/`)
if (error.value || !service.value) throw createError({ statusCode: error.value?.statusCode === 404 ? 404 : 503, statusMessage: 'Услуга недоступна' })
const { data: projects } = await useApi<Paginated<Project>>('/projects/', { query: { service: route.params.slug } })
usePageSeo(() => service.value?.seo_title || `${service.value?.title} в Волгограде`, () => service.value?.seo_description || service.value?.summary || '')
useStructuredData(() => ({
  '@context': 'https://schema.org', '@type': 'Service', name: service.value?.title,
  description: service.value?.description, areaServed: 'Волгоградская область',
  provider: { '@type': 'Organization', name: settings.value?.company_name, url: config.public.siteUrl },
}))
</script>
<template><div v-if="service"><section class="container section-pad"><Breadcrumbs :items="[{ label: 'Услуги', to: '/services' }, { label: service.title }]" /><div class="page-heading"><span class="eyebrow">ИНЖЕНЕРНЫЕ УСЛУГИ / ВОЛГОГРАД</span><h1>{{ service.title }}</h1><p>{{ service.summary }}</p><a href="#request" class="button">Обсудить задачу ↗</a></div><div class="story-grid"><h2>Решение начинается<br>с понимания задачи.</h2><div class="prose"><p>{{ service.description }}</p><h3>Где применяется</h3><p>{{ service.applications }}</p></div></div><div v-if="service.materials.length" class="detail-section"><h2>Подходящие материалы.</h2><div class="material-tags compact"><NuxtLink v-for="material in service.materials" :key="material.id" :to="`/materials/${material.slug}`">{{ material.name }} ↗</NuxtLink></div></div><div class="detail-section" v-if="service.faq.length"><h2>Частые вопросы.</h2><div class="faq-list"><details v-for="(faq, index) in service.faq" :key="index"><summary>{{ faq.question }}<span>+</span></summary><p>{{ faq.answer }}</p></details></div></div></section><section v-if="projects?.results.length" class="portfolio-section section-pad"><div class="container"><div class="section-heading"><h2>Примеры проектов.</h2><NuxtLink :to="{ path: '/projects', query: { service: service.slug } }">Все проекты ↗</NuxtLink></div><div class="project-grid"><ProjectCard v-for="project in projects.results.slice(0, 3)" :key="project.id" :project="project" /></div></div></section><LeadForm :service-id="service.id" /></div></template>
