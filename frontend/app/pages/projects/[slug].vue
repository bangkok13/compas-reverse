<script setup lang="ts">
import type { Project } from '~/types'
const route = useRoute()
const { data: project, error } = await useApi<Project>(`/projects/${route.params.slug}/`)
if (error.value || !project.value) throw createError({ statusCode: error.value?.statusCode === 404 ? 404 : 503, statusMessage: error.value?.statusCode === 404 ? 'Проект не найден' : 'Не удалось загрузить проект' })
const before = computed(() => project.value?.images.find(i => i.role === 'before'))
const after = computed(() => project.value?.images.find(i => i.role === 'after'))
const showViewer = ref(false)
usePageSeo(() => project.value?.seo_title || `${project.value?.title} — 3D-мастерская`, () => project.value?.seo_description || project.value?.summary || '', () => project.value?.cover || '')
</script>
<template>
  <div v-if="project">
    <section class="container section-pad"><Breadcrumbs :items="[{ label: 'Наши работы', to: '/projects' }, { label: project.title }]" /><div class="page-heading"><span class="eyebrow">{{ project.category.name }}</span><h1>{{ project.title }}</h1><p>{{ project.summary }}</p></div><p v-if="project.is_demo" class="demo-notice">Демонстрационный пример. Изображения — иллюстрации, а не фотографии выполненного заказа.</p><img v-if="project.cover" class="project-cover" :src="project.cover" :alt="project.title" width="1200" height="900" fetchpriority="high"><div class="project-facts"><div><span>МАТЕРИАЛ</span><strong>{{ project.material?.name || 'Индивидуальный подбор' }}</strong></div><div><span>ТЕХНОЛОГИЯ</span><strong>{{ project.technology || 'По задаче' }}</strong></div><div v-if="project.completed_at"><span>ДАТА ВЫПОЛНЕНИЯ</span><strong>{{ new Date(project.completed_at).toLocaleDateString('ru-RU') }}</strong></div></div>
    <div class="story-grid"><div><span class="eyebrow">О ПРОЕКТЕ</span><h2>От задачи<br>к результату.</h2></div><div class="prose"><p v-if="project.description">{{ project.description }}</p><template v-for="(block, index) in [{ title: 'Задача', text: project.problem }, { title: 'Решение', text: project.solution }, { title: 'Результат', text: project.result }]" :key="index"><h3 v-if="block.text">{{ block.title }}</h3><p v-if="block.text">{{ block.text }}</p></template></div></div>
    <div v-if="before && after" class="detail-section"><span class="eyebrow">СРАВНЕНИЕ</span><h2>До и после.</h2><BeforeAfter :before="before.image" :after="after.image" /></div>
    <div v-if="project.images.length" class="detail-section"><h2>В деталях.</h2><ProjectGallery :images="project.images" /></div>
    <div v-if="project.model_url && project.model_format" class="detail-section"><h2>Рассмотрите со всех сторон.</h2><ClientOnly><LazyModelViewer v-if="showViewer" :src="project.model_url" :format="project.model_format" /><button v-else class="viewer-placeholder" @click="showViewer = true"><span>◇</span>Открыть 3D-модель<small>Вращение и масштабирование</small></button></ClientOnly></div>
    <a v-if="project.video_url" :href="project.video_url" class="button button-outline" target="_blank" rel="noopener noreferrer">Смотреть видео проекта ↗</a>
    <div v-if="project.services.length" class="related-links"><span class="eyebrow">УСЛУГИ В ПРОЕКТЕ</span><NuxtLink v-for="service in project.services" :key="service.id" :to="`/services/${service.slug}`">{{ service.title }} ↗</NuxtLink></div>
    </section><LeadForm />
  </div>
</template>
