<script setup lang="ts">defineProps<{ retry?: () => unknown }>()</script>
<template><div class="empty-state" role="alert"><h2>Не удалось загрузить данные</h2><p>Попробуйте обновить страницу немного позже.</p><button v-if="retry" class="button button-outline" @click="retry()">Повторить загрузку</button></div></template>
