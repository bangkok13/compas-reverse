<script setup lang="ts">
import type { ProjectImage } from '~/types'
const props = defineProps<{ images: ProjectImage[] }>()
const dialog = ref<HTMLDialogElement>()
const active = ref(0)
const current = computed(() => props.images[active.value])
function open(index: number) { active.value = index; dialog.value?.showModal() }
function step(delta: number) { active.value = (active.value + delta + props.images.length) % props.images.length }
function keys(event: KeyboardEvent) {
  if (event.key === 'ArrowRight') step(1)
  if (event.key === 'ArrowLeft') step(-1)
}
</script>
<template>
  <div v-if="images.length" class="gallery-grid"><button v-for="(image, index) in images" :key="image.id" class="gallery-item" @click="open(index)"><img :src="image.thumbnail || image.image" :alt="image.caption || `Фотография ${index + 1}`" loading="lazy" width="1000" height="750"><span>{{ image.caption || 'Открыть фотографию' }} ↗</span></button></div>
  <dialog ref="dialog" class="lightbox" aria-label="Галерея проекта" @keydown="keys" @click="($event.target === dialog) && dialog?.close()">
    <div v-if="current" class="lightbox-inner"><button class="lightbox-close" autofocus aria-label="Закрыть галерею" @click="dialog?.close()">✕</button><img :src="current.image" :alt="current.caption || 'Фотография проекта'"><div class="lightbox-controls"><button aria-label="Предыдущая фотография" @click="step(-1)">←</button><span>{{ current.caption }} · {{ active + 1 }} / {{ images.length }}</span><button aria-label="Следующая фотография" @click="step(1)">→</button></div></div>
  </dialog>
</template>
