<script setup lang="ts">
defineProps<{ before: string; after: string }>()
const amount = ref(50)
</script>
<template><div class="comparison"><img :src="before" alt="Деталь до восстановления" loading="lazy" width="1200" height="900"><img class="comparison-after" :src="after" alt="Деталь после восстановления" loading="lazy" width="1200" height="900" :style="{ clipPath: `inset(0 0 0 ${amount}%)` }"><div class="comparison-line" :style="{ left: `${amount}%` }"><span>↔</span></div><span class="compare-before-label">До</span><span class="compare-after-label">После</span><input v-model="amount" type="range" min="0" max="100" aria-label="Сравнить деталь до и после восстановления"></div></template>
