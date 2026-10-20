<script setup lang="ts">
import type { Project } from '~/types'
defineProps<{ project: Project }>()
</script>
<template>
  <NuxtLink :to="`/projects/${project.slug}`" class="project-card">
    <div class="project-image"><img v-if="project.thumbnail || project.cover" :src="project.thumbnail || project.cover" :alt="project.title" loading="lazy" width="1000" height="750"><div v-else class="image-placeholder">3D<span>Изображение проекта</span></div><span v-if="project.is_demo" class="demo-badge">Демонстрационный пример</span><span class="card-arrow">↗</span></div>
    <div class="project-meta"><span>{{ project.category.name }}</span><span>{{ project.material?.name || project.technology }}</span></div>
    <h3>{{ project.title }}</h3><p>{{ project.summary }}</p>
  </NuxtLink>
</template>
