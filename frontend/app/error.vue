<script setup lang="ts">
import type { NuxtError } from '#app'
defineProps<{ error: NuxtError }>()
</script>
<template><main class="container error-page"><span class="eyebrow">3D ENGINEERING</span><p class="error-code">{{ error.statusCode }}</p><h1>{{ error.statusCode === 404 ? 'Эта страница не найдена.' : 'Не удалось открыть страницу.' }}</h1><p>Попробуйте перейти на главную или вернуться немного позже.</p><button class="button" @click="clearError({ redirect: '/' })">На главную ↗</button></main></template>
