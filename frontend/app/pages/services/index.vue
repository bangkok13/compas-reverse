<script setup lang="ts">
import type { Service } from '~/types'
const { data, error, refresh } = await useApi<Service[]>('/services/')
usePageSeo(() => 'Услуги 3D-мастерской в Волгограде', () => '3D-печать, сканирование, CAD-моделирование, реверс-инжиниринг, восстановление деталей и малые серии.')
</script>
<template><div><section class="container section-pad"><Breadcrumbs :items="[{ label: 'Услуги' }]" /><div class="page-heading"><span class="eyebrow">ТЕХНОЛОГИИ И ВОЗМОЖНОСТИ</span><h1>Одна мастерская.<br>Весь путь до детали.</h1><p>Подключаемся на любом этапе: от идеи и повреждённого образца до готовой модели для печати.</p></div><ApiError v-if="error" :retry="refresh" /><div v-else class="service-grid"><NuxtLink v-for="(service, index) in data" :key="service.id" :to="`/services/${service.slug}`" class="service-card"><div class="service-card-top"><span class="service-number">0{{ index + 1 }}</span><span class="service-arrow">↗</span></div><h2>{{ service.title }}</h2><p>{{ service.summary }}</p></NuxtLink></div></section><LeadForm /></div></template>
