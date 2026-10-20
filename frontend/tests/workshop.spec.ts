import { test, expect } from '@playwright/test'

const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAIAAAAC64paAAAALElEQVR4nGNkYPjPQC5gIlsnw6hmkgET6VoQYFQziYCJVA3IYFQziYCiAAMAIJ4BJwS5UI4AAAAASUVORK5CYII=', 'base64')

test('главная, адаптивность, навигация и SSR', async ({ page, request }, info) => {
  const errors: string[] = []
  page.on('pageerror', error => errors.push(error.message))
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Восстанавливаем детали')
  await expect(page.locator('.service-card')).toHaveCount(6)
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1)
  expect(overflow).toBe(false)
  await page.screenshot({ path: `test-results/home-${info.project.name}.png`, fullPage: true })
  if (info.project.name === 'mobile') {
    await page.getByRole('button', { name: 'Меню', exact: true }).click()
    await page.locator('#mobile-menu').getByRole('link', { name: 'Наши работы', exact: true }).click()
  } else await page.locator('.desktop-nav').getByRole('link', { name: 'Наши работы', exact: true }).click()
  await expect(page).toHaveURL(/\/projects$/)
  const html = await (await request.get('/services/3d-printing')).text()
  expect(html).toContain('3D-печать')
  expect(html).toContain('application/ld+json')
  expect(html).toContain('rel="canonical"')
  expect(errors).toEqual([])
})

test('категории, поиск, галерея и сравнение', async ({ page }) => {
  await page.goto('/projects')
  await page.getByRole('button', { name: 'Корпуса электроники', exact: true }).click()
  await expect(page.locator('.project-card')).toHaveCount(1)
  await page.locator('.project-card').click()
  await expect(page.getByRole('heading', { level: 1 })).toContainText('Корпус')
  await expect(page.getByLabel('Сравнить деталь до и после восстановления')).toBeVisible()
  await page.getByLabel('Сравнить деталь до и после восстановления').fill('70')
  await page.locator('.gallery-item').first().click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await page.getByRole('button', { name: 'Следующая фотография' }).click()
  await page.getByRole('button', { name: 'Закрыть галерею' }).click()
  await expect(page.getByRole('dialog')).not.toBeVisible()
  await page.goto('/projects')
  await page.getByRole('searchbox').fill('Несуществующая деталь XYZ')
  await page.getByRole('button', { name: 'Найти', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Проекты не найдены' })).toBeVisible()
})

test('заявка с фотографией сохраняется и не повторяется при обновлении', async ({ page }) => {
  await page.goto('/#request')
  await page.getByLabel('Ваше имя').fill('Демонстрационный клиент E2E')
  await page.getByLabel('Телефон', { exact: false }).fill('+7 999 000 00 00')
  await page.getByLabel('Расскажите о задаче').fill('Тестовая заявка: изготовить корпус 100 × 60 мм.')
  await page.locator('input[type=file]').setInputFiles({ name: 'test-part.png', mimeType: 'image/png', buffer: png })
  await page.locator('input[name=consent]').check()
  const responsePromise = page.waitForResponse(response => response.url().endsWith('/api/leads/') && response.request().method() === 'POST')
  await page.getByRole('button', { name: 'Отправить на расчёт' }).click()
  const response = await responsePromise
  expect(response.status(), await response.text()).toBe(201)
  await expect(page.getByRole('heading', { name: 'Заявка отправлена' })).toBeVisible()
  const reference = await page.locator('.reference').textContent()
  await page.reload()
  await expect(page.locator('.reference')).toHaveText(reference!)
  await expect(page.getByRole('button', { name: 'Отправить на расчёт' })).toHaveCount(0)
})

test('новый проект с несколькими фото публикуется из Django Admin', async ({ page }, info) => {
  test.skip(info.project.name !== 'desktop', 'Админский сценарий выполняется один раз.')
  test.skip(!process.env.E2E_ADMIN_PASSWORD, 'Требуются локальные тестовые учётные данные.')
  const adminBase = process.env.E2E_ADMIN_URL || 'http://127.0.0.1:8000'
  const slug = `e2e-project-${Date.now()}`
  await page.goto(`${adminBase}/admin/login/`)
  await page.locator('#id_username').fill(process.env.E2E_ADMIN_USER || 'e2e')
  await page.locator('#id_password').fill(process.env.E2E_ADMIN_PASSWORD!)
  await page.locator('input[type=submit]').click()
  await page.goto(`${adminBase}/admin/portfolio/project/add/`)
  await page.locator('#id_title').fill('Демонстрационный проект E2E')
  await page.locator('#id_slug').click()
  await page.locator('#id_slug').fill(slug)
  await page.locator('#id_slug').press('Tab')
  await expect(page.locator('#id_slug')).toHaveValue(slug)
  await page.locator('#id_category').selectOption({ label: 'Прототипирование' })
  await page.locator('#id_summary').fill('Тест публикации из административного интерфейса.')
  await page.locator('#id_status').selectOption('published')
  await page.locator('#id_is_demo').check()
  await page.locator('#id_cover').setInputFiles({ name: 'cover.png', mimeType: 'image/png', buffer: png })
  await page.locator('#id_upload_images').setInputFiles([
    { name: 'first.png', mimeType: 'image/png', buffer: png },
    { name: 'second.png', mimeType: 'image/png', buffer: png },
  ])
  await page.locator('#id_model_file').setInputFiles({
    name: 'demo.stl', mimeType: 'application/octet-stream',
    buffer: Buffer.from('solid demo\nfacet normal 0 0 1\nouter loop\nvertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\nendloop\nendfacet\nendsolid demo'),
  })
  await page.locator('#id_viewer_enabled').check()
  await page.locator('input[name=_save]').first().click()
  await expect(page.locator('.success')).toBeVisible()
  await page.goto(`/projects/${slug}`)
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Демонстрационный проект E2E')
  await expect(page.locator('.gallery-item')).toHaveCount(2)
  await expect(page.locator('.viewer-canvas canvas')).toHaveCount(0)
  const modelResponse = page.waitForResponse(response => response.url().endsWith(`/${slug}/model/`))
  await page.getByRole('button', { name: 'Открыть 3D-модель', exact: false }).click()
  expect((await modelResponse).status()).toBe(200)
  await expect(page.locator('.viewer-canvas canvas')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Сбросить вид' })).toBeVisible()
})

test('служебные страницы и корректный 404', async ({ request }) => {
  const sitemap = await request.get('/sitemap.xml')
  expect(sitemap.status()).toBe(200)
  expect(await sitemap.text()).toContain('/services/3d-printing')
  expect(await (await request.get('/robots.txt')).text()).toContain('Disallow: /')
  expect((await request.get('/projects/not-a-real-project')).status()).toBe(404)
  expect((await request.get('/privacy')).status()).toBe(200)
})
