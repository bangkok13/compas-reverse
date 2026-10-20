<script setup lang="ts">
import type { Service } from '~/types'
const props = defineProps<{ serviceId?: number }>()
const settings = useSiteSettings()
const { data: services } = await useApi<Service[]>('/services/')
const form = reactive({
  name: '', phone: '', email: '', service: props.serviceId ? String(props.serviceId) : '',
  description: '', dimensions: '', quantity: 1, material: '', deadline: '', consent: false, website: '',
})
const files = ref<File[]>([])
const error = ref('')
const fieldErrors = ref<Record<string, string[]>>({})
const busy = ref(false)
const reference = ref('')
const fileInput = ref<HTMLInputElement>()
let idempotencyKey = ''
onMounted(() => {
  try { reference.value = sessionStorage.getItem('last-lead-reference') || '' } catch { /* Storage is optional. */ }
})
function addFiles(event: Event) {
  const incoming = Array.from((event.target as HTMLInputElement).files || [])
  const combined = [...files.value, ...incoming]
  const allowed = /\.(jpe?g|png|webp|pdf|stl|step|stp|obj|3mf|zip)$/i
  if (combined.length > 8 || combined.reduce((sum, f) => sum + f.size, 0) > 50 * 1024 * 1024) {
    error.value = 'Можно приложить до 8 файлов, суммарно не более 50 МБ.'
  } else if (incoming.some(f => f.size > 20 * 1024 * 1024 || !allowed.test(f.name))) {
    error.value = 'Проверьте форматы файлов. Каждый файл должен быть не больше 20 МБ.'
  } else {
    files.value = combined
    error.value = ''
  }
  if (fileInput.value) fileInput.value.value = ''
}
async function submit() {
  if (busy.value) return
  busy.value = true
  error.value = ''
  fieldErrors.value = {}
  try {
    if (!idempotencyKey) idempotencyKey = crypto.randomUUID()
    const { csrfToken } = await $fetch<{ csrfToken: string }>('/api/csrf/')
    const body = new FormData()
    Object.entries(form).forEach(([key, value]) => {
      if (value !== '' && value !== undefined) body.append(key, String(value))
    })
    body.append('idempotency_key', idempotencyKey)
    body.append('consent_version', settings.value?.consent_version || '')
    files.value.forEach(file => body.append('files', file))
    const result = await $fetch<{ reference: string }>('/api/leads/', {
      method: 'POST', body, headers: { 'X-CSRFToken': csrfToken },
    })
    reference.value = result.reference
    try { sessionStorage.setItem('last-lead-reference', result.reference) } catch { /* Storage is optional. */ }
    files.value = []
    form.name = form.phone = form.email = form.description = form.dimensions = form.material = ''
    form.deadline = ''
    form.consent = false
  } catch (e: unknown) {
    const failure = e as { data?: Record<string, unknown>; status?: number; statusCode?: number }
    const data = failure.data
    if (data && typeof data === 'object') {
      fieldErrors.value = Object.fromEntries(Object.entries(data).filter(([, value]) => Array.isArray(value))) as Record<string, string[]>
      error.value = typeof data.detail === 'string' ? data.detail : Object.values(fieldErrors.value).flat().join(' ') || 'Не удалось отправить заявку. Попробуйте ещё раз.'
    } else error.value = 'Нет связи с сервером. Проверьте подключение и повторите отправку.'
    // A validation error never creates a lead. A lost response may have done so:
    // preserve the key on network/server errors for safe retries.
    if ([400, 409].includes(failure.statusCode || failure.status || 0)) idempotencyKey = ''
  } finally { busy.value = false }
}
function reset() {
  reference.value = ''
  idempotencyKey = ''
  try { sessionStorage.removeItem('last-lead-reference') } catch { /* Storage is optional. */ }
}
</script>

<template>
  <section id="request" class="request-section section-pad">
    <div class="container request-grid">
      <div class="request-intro">
        <span class="eyebrow"><span class="mini-cross">+</span> НАЧНЁМ С ВАШЕЙ ЗАДАЧИ</span>
        <h2>Есть деталь.<br>Нужно <span class="blue-text">решение.</span></h2>
        <p>Пришлите фотографию, модель или просто расскажите, что нужно сделать. Обсудим способ изготовления, материал и стоимость.</p>
        <div class="request-note"><span>↗</span><p>Нет чертежа или 3D-модели?<br><strong>Можно начать с образца.</strong></p></div>
        <div class="accepted-files"><span class="eyebrow">МОЖНО ПРИЛОЖИТЬ</span><p>Фотографию · Чертёж · 3D-модель</p><small>JPG, PNG, WebP, PDF, STL, STEP, STP, OBJ, 3MF, ZIP</small></div>
      </div>
      <div class="request-panel">
        <div v-if="reference" class="success-panel" role="status">
          <span class="success-icon">✓</span><h3>Заявка отправлена</h3><p>Ваш номер:</p><strong class="reference">{{ reference }}</strong><p>Сохраняйте номер для дальнейшего обсуждения задачи.</p><button class="button" @click="reset">Отправить новую заявку ↗</button>
        </div>
        <div v-else-if="settings && !settings.accept_leads" class="empty-state"><h3>Приём заявок временно приостановлен</h3><p>Свяжитесь с мастерской по контактам на сайте.</p><NuxtLink to="/contacts" class="button">Контакты ↗</NuxtLink></div>
        <form v-else @submit.prevent="submit">
          <h3>Рассчитать стоимость изготовления</h3><p class="form-caption">Поля со звёздочкой обязательны</p>
          <div class="form-grid">
            <label>Ваше имя *<input v-model="form.name" name="name" autocomplete="name" required minlength="2" maxlength="120" placeholder="Как к вам обращаться" :aria-invalid="!!fieldErrors.name"></label>
            <label>Телефон *<input v-model="form.phone" name="phone" type="tel" autocomplete="tel" required maxlength="40" placeholder="+7 ___ ___-__-__" :aria-invalid="!!fieldErrors.phone"></label>
            <label>Email<input v-model="form.email" type="email" name="email" autocomplete="email" placeholder="Для ответа и файлов" maxlength="254"></label>
            <label>Что нужно сделать<select v-model="form.service" name="service"><option value="">Помогите определиться</option><option v-for="service in services" :key="service.id" :value="service.id">{{ service.title }}</option></select></label>
            <label class="full-width">Расскажите о задаче *<textarea v-model="form.description" name="description" rows="4" required minlength="10" maxlength="10000" placeholder="Что за деталь, где используется и что нужно получить?" :aria-invalid="!!fieldErrors.description" /></label>
          </div>
          <details class="form-details"><summary>Размеры, материал и сроки <span>+</span></summary>
            <div class="form-grid">
              <label>Размеры детали<input v-model="form.dimensions" name="dimensions" placeholder="Например, 100 × 60 × 30 мм" maxlength="200"></label>
              <label>Количество<input v-model="form.quantity" name="quantity" type="number" min="1" max="100000"></label>
              <label>Материал<input v-model="form.material" name="material" placeholder="Если уже знаете" maxlength="100"></label>
              <label>Желаемый срок<input v-model="form.deadline" name="deadline" type="date"></label>
            </div>
          </details>
          <label class="file-upload"><span class="upload-icon">↥</span><strong>Прикрепить фотографии или файлы</strong><small>До 8 файлов · до 20 МБ каждый · 50 МБ суммарно</small><input ref="fileInput" type="file" name="files" multiple accept=".jpg,.jpeg,.png,.webp,.pdf,.stl,.step,.stp,.obj,.3mf,.zip" @change="addFiles"></label>
          <ul v-if="files.length" class="file-list"><li v-for="(file, i) in files" :key="`${file.name}-${i}`"><span>{{ file.name }} <small>{{ (file.size / 1024 / 1024).toFixed(2) }} МБ</small></span><button type="button" :aria-label="`Удалить ${file.name}`" @click="files.splice(i, 1)">✕</button></li></ul>
          <label class="honeypot" aria-hidden="true">Сайт<input v-model="form.website" name="website" tabindex="-1" autocomplete="off"></label>
          <label class="consent-label"><input v-model="form.consent" name="consent" type="checkbox" required><span>Даю <NuxtLink to="/consent" target="_blank">согласие на обработку персональных данных</NuxtLink> и ознакомлен(а) с <NuxtLink to="/privacy" target="_blank">политикой конфиденциальности</NuxtLink>.</span></label>
          <p v-if="error" class="form-error" role="alert">{{ error }}</p>
          <button type="submit" class="button submit-button" :disabled="busy">{{ busy ? 'Отправляем заявку…' : 'Отправить на расчёт' }} <span v-if="!busy">↗</span></button>
          <p class="form-footnote">Стоимость и возможность изготовления определяются после изучения задачи.</p>
        </form>
      </div>
    </div>
  </section>
</template>
