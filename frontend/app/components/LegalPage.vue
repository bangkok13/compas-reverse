<script setup lang="ts">
const props = defineProps<{ kind: 'privacy' | 'consent' }>()
const settings = useSiteSettings()
const title = computed(() => props.kind === 'privacy' ? 'Политика конфиденциальности' : 'Согласие на обработку персональных данных')
usePageSeo(() => title.value, () => title.value)
useSeoMeta({ robots: 'noindex, follow' })
</script>
<template><section class="container section-pad legal-page"><Breadcrumbs :items="[{ label: title }]" /><h1>{{ title }}</h1><p v-if="!settings?.legal_reviewed" class="demo-notice">Шаблон для последующего заполнения и юридической проверки. Не является готовым документом для публикации.</p><div class="prose"><p>{{ (kind === 'privacy' ? settings?.privacy_text : settings?.consent_text) || 'Документ готовится. Свяжитесь с мастерской для уточнения информации.' }}</p></div></section></template>
