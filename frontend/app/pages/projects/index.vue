<script setup lang="ts">
import type { Category, Paginated, Project } from '~/types'
const route = useRoute()
const router = useRouter()
const category = computed(() => typeof route.query.category === 'string' ? route.query.category : '')
const page = computed(() => Math.max(1, Number(route.query.page) || 1))
const search = ref(typeof route.query.search === 'string' ? route.query.search : '')
const { data: categories } = await useApi<Category[]>('/categories/')
const { data, error, status, refresh } = await useApi<Paginated<Project>>('/projects/', {
  query: computed(() => ({ category: category.value, page: page.value, search: route.query.search || '', service: route.query.service || '', material: route.query.material || '' })),
})
function filter(value: string) { router.push({ query: { ...route.query, category: value || undefined, page: undefined } }) }
function find() { router.push({ query: { ...route.query, search: search.value || undefined, page: undefined } }) }
usePageSeo(() => 'Наши работы — проекты 3D-мастерской', () => 'Портфолио 3D-печати, восстановления деталей и реверс-инжиниринга в Волгограде.')
</script>
<template>
  <div class="light-page"><div class="container section-pad">
    <Breadcrumbs :items="[{ label: 'Наши работы' }]" />
    <div class="page-heading"><span class="eyebrow">ПОРТФОЛИО МАСТЕРСКОЙ</span><h1>Решения, которые<br>можно взять в руки.</h1><p>От сломанного образца до функциональной детали.<br>Задачи, технологии и результаты нашей работы.</p></div>
    <div class="portfolio-controls"><div class="filter-tabs" aria-label="Категории проектов"><button :class="{ active: !category }" :aria-pressed="!category" @click="filter('')">Все работы</button><button v-for="item in categories" :key="item.id" :class="{ active: category === item.slug }" :aria-pressed="category === item.slug" @click="filter(item.slug)">{{ item.name }}</button></div><form class="search-form" @submit.prevent="find"><input v-model="search" type="search" aria-label="Поиск проектов" placeholder="Найти проект"><button type="submit" aria-label="Найти">→</button></form></div>
    <ApiError v-if="error" :retry="refresh" />
    <div v-else :aria-busy="status === 'pending'"><p class="results-count">{{ data?.count || 0 }} проектов</p><div v-if="data?.results.length" class="project-grid"><ProjectCard v-for="project in data.results" :key="project.id" :project="project" /></div><div v-else class="empty-state"><h2>Проекты не найдены</h2><p>Попробуйте другую категорию или измените запрос.</p><button class="button" @click="search = ''; router.push('/projects')">Сбросить фильтры</button></div>
    <nav v-if="data && data.count > 12" class="pagination" aria-label="Страницы портфолио"><NuxtLink v-if="page > 1" :to="{ query: { ...route.query, page: page - 1 } }">← Назад</NuxtLink><span>Страница {{ page }} из {{ Math.ceil(data.count / 12) }}</span><NuxtLink v-if="data.next" :to="{ query: { ...route.query, page: page + 1 } }">Далее →</NuxtLink></nav></div>
  </div><LeadForm /></div>
</template>
