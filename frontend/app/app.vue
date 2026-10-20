<script setup lang="ts">
import type { SiteSettings } from '~/types'
const settings = useSiteSettings()
const { data } = await useApi<SiteSettings>('/settings/')
settings.value = data.value ?? null
const menuOpen = ref(false)
const route = useRoute()
watch(() => route.fullPath, () => { menuOpen.value = false })
const nav = [
  { to: '/services', label: 'Услуги' },
  { to: '/projects', label: 'Наши работы' },
  { to: '/materials', label: 'Материалы' },
  { to: '/contacts', label: 'Контакты' },
]
</script>

<template>
  <div>
    <a class="skip-link" href="#main">Перейти к содержимому</a>
    <header class="site-header">
      <div class="container header-inner">
        <NuxtLink to="/" class="brand" aria-label="На главную">
          <img v-if="settings?.logo" :src="settings.logo" width="40" height="40" alt="">
          <svg v-else viewBox="0 0 44 44" width="44" height="44" aria-hidden="true"><path d="M22 3 40 13v18L22 41 4 31V13Z" fill="none" stroke="currentColor" stroke-width="2"/><path d="m4 13 18 10 18-10M22 23v18M13 8l18 10v10l-9 5-9-5V18l9-5" fill="none" stroke="#4685ff" stroke-width="2"/></svg>
          <span>{{ settings?.company_name || '3D Engineering Volgograd' }}</span>
        </NuxtLink>
        <nav class="desktop-nav" aria-label="Основная навигация">
          <NuxtLink v-for="item in nav" :key="item.to" :to="item.to">{{ item.label }}</NuxtLink>
        </nav>
        <NuxtLink class="button button-small header-cta" to="/#request">Обсудить задачу <span>↗</span></NuxtLink>
        <button class="menu-toggle" :aria-expanded="menuOpen" aria-controls="mobile-menu" aria-label="Меню" @click="menuOpen = !menuOpen">{{ menuOpen ? '✕' : '☰' }}</button>
      </div>
      <nav v-if="menuOpen" id="mobile-menu" class="mobile-nav" aria-label="Мобильная навигация">
        <NuxtLink v-for="item in nav" :key="item.to" :to="item.to">{{ item.label }}</NuxtLink>
        <NuxtLink to="/#request">Рассчитать стоимость ↗</NuxtLink>
      </nav>
    </header>
    <main id="main"><NuxtPage /></main>
    <footer class="site-footer">
      <div class="container">
        <div class="footer-top">
          <div><NuxtLink to="/" class="footer-brand">{{ settings?.company_name || '3D Engineering Volgograd' }}</NuxtLink><p>Инженерный подход.<br>Осязаемый результат.</p></div>
          <div class="footer-links"><NuxtLink v-for="item in nav" :key="item.to" :to="item.to">{{ item.label }}</NuxtLink></div>
          <div><span class="eyebrow">Работаем с вашим регионом</span><p>{{ settings?.region }}</p><a v-if="settings?.email" :href="`mailto:${settings.email}`">{{ settings.email }} ↗</a><NuxtLink v-else to="/#request">Отправить задачу ↗</NuxtLink></div>
        </div>
        <div class="footer-bottom"><span>© {{ new Date().getFullYear() }} {{ settings?.company_name }}</span><NuxtLink to="/privacy">Политика конфиденциальности</NuxtLink><NuxtLink to="/consent">Обработка персональных данных</NuxtLink></div>
      </div>
    </footer>
  </div>
</template>
