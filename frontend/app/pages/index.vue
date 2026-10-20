<script setup lang="ts">
import type { Service, Project, Paginated, Material } from '~/types'
const settings = useSiteSettings()
const [{ data: services }, { data: projects }, { data: materials }] = await Promise.all([
  useApi<Service[]>('/services/'),
  useApi<Paginated<Project>>('/projects/', { query: { featured: 'true' } }),
  useApi<Material[]>('/materials/'),
])
usePageSeo(() => settings.value?.seo_title || '3D-мастерская в Волгограде', () => settings.value?.seo_description || '')
const config = useRuntimeConfig()
useStructuredData(() => ({
  '@context': 'https://schema.org', '@type': settings.value?.address ? 'LocalBusiness' : 'Organization',
  name: settings.value?.company_name, url: config.public.siteUrl,
  ...(settings.value?.address ? { address: settings.value.address } : {}),
  ...(settings.value?.phone ? { telephone: settings.value.phone } : {}),
  ...(settings.value?.email ? { email: settings.value.email } : {}),
}))
</script>

<template>
  <div>
    <section class="hero container">
      <div class="hero-copy">
        <div class="eyebrow"><span class="status-dot" /> ИНЖЕНЕРНАЯ 3D-МАСТЕРСКАЯ</div>
        <h1>{{ settings?.hero_title || 'Восстанавливаем детали, которых больше нет в продаже.' }}</h1>
        <p class="hero-description">{{ settings?.hero_subtitle }}</p>
        <div class="hero-actions"><a href="#request" class="button">Рассчитать стоимость <span>↗</span></a><NuxtLink to="/projects" class="text-link">Посмотреть наши работы <span>→</span></NuxtLink></div>
        <div class="hero-location"><svg viewBox="0 0 20 20" width="18" height="18" fill="none" stroke="currentColor" aria-hidden="true"><path d="M16 8c0 5-6 10-6 10S4 13 4 8a6 6 0 1 1 12 0Z"/><circle cx="10" cy="8" r="2"/></svg>{{ settings?.region }}</div>
      </div>
      <EngineeringVisual />
    </section>
    <div class="capabilities-strip"><div class="container"><span>ОТ ИДЕИ ДО ГОТОВОЙ ДЕТАЛИ</span><span>3D-сканирование</span><i>↗</i><span>CAD-модель</span><i>↗</i><span>Инженерный пластик</span><i>↗</i><span>Функциональное изделие</span></div></div>
    <section class="section-pad container">
      <div class="section-heading"><div><span class="eyebrow">01 / НАПРАВЛЕНИЯ РАБОТЫ</span><h2>Технологии под вашу задачу.</h2></div><p>Восстановить старое.<br>Разработать новое. Изготовить серию.</p></div>
      <div class="service-grid">
        <NuxtLink v-for="(service, index) in services" :key="service.id" :to="`/services/${service.slug}`" class="service-card"><div class="service-card-top"><span class="service-number">{{ String(index + 1).padStart(2, '0') }}</span><span class="service-glyph" aria-hidden="true">{{ ['◇', '⌖', '⤢', '⌁', '⊞', '▱'][index % 6] }}</span><span class="service-arrow">↗</span></div><h3>{{ service.title }}</h3><p>{{ service.summary }}</p></NuxtLink>
      </div>
    </section>
    <section class="portfolio-section section-pad">
      <div class="container"><div class="section-heading"><div><span class="eyebrow">02 / ОТ ЗАДАЧИ К РЕЗУЛЬТАТУ</span><h2>Детали. И истории за ними.</h2></div><NuxtLink to="/projects" class="text-link">Все работы <span>↗</span></NuxtLink></div>
        <div v-if="projects?.results.length" class="project-grid"><ProjectCard v-for="project in projects.results.slice(0, 3)" :key="project.id" :project="project" /></div>
        <div v-else class="empty-state"><p>Здесь появятся опубликованные проекты мастерской.</p></div>
      </div>
    </section>
    <section class="section-pad container process-section">
      <div class="section-heading"><div><span class="eyebrow">03 / ПРОЦЕСС</span><h2>Понятный путь<br>к готовой детали.</h2></div><p>Даже если всё, что у вас есть, —<br>сломанный образец и идея.</p></div>
      <div class="process-grid"><div v-for="(step, index) in settings?.process" :key="index" class="process-step"><div class="step-number">{{ String(index + 1).padStart(2, '0') }}<span>↗</span></div><h3>{{ step.title }}</h3><p>{{ step.text }}</p></div></div>
    </section>
    <section class="materials-band"><div class="container materials-band-inner"><div><span class="eyebrow">04 / МАТЕРИАЛЫ</span><h2>Форма важна.<br>Свойства — тоже.</h2><p>Подбираем пластик под условия работы детали.<br>Учитываем нагрузки, среду и ограничения печати.</p><NuxtLink to="/materials" class="text-link">Сравнить материалы <span>↗</span></NuxtLink></div><div class="material-tags"><NuxtLink v-for="material in materials" :key="material.id" :to="`/materials/${material.slug}`">{{ material.name }}<span>↗</span></NuxtLink><small>Свойства зависят от марки материала и условий изготовления.</small></div></div></section>
    <section class="section-pad container"><div class="section-heading"><div><span class="eyebrow">05 / ПОДХОД МАСТЕРСКОЙ</span><h2>Сначала думаем.<br>Потом печатаем.</h2></div></div><div class="advantages-grid"><div v-for="(item, index) in settings?.advantages" :key="index"><span class="blue-text">+ {{ String(index + 1).padStart(2, '0') }}</span><h3>{{ item.title }}</h3><p>{{ item.text }}</p></div></div><div class="business-block"><div><span class="eyebrow">ДЛЯ КОМПАНИЙ И ПРОИЗВОДСТВ</span><h3>Ваше техническое задание.<br>Наш инженерный подход.</h3></div><div><p>{{ settings?.business_text }}</p><a href="#request" class="text-link">Обсудить сотрудничество ↗</a></div></div></section>
    <LeadForm />
    <section class="contact-strip container"><span class="eyebrow">БЛИЖЕ, ЧЕМ КАЖЕТСЯ</span><h2>В Волгограде.<br>Для задач по всей России.</h2><NuxtLink to="/contacts" class="button button-outline">Связаться с мастерской ↗</NuxtLink></section>
  </div>
</template>
