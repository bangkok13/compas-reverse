import { chromium } from '../frontend/node_modules/playwright/index.mjs'
import { mkdir } from 'node:fs/promises'
import { resolve } from 'node:path'

const output = resolve('.runtime/previews')
await mkdir(output, { recursive: true })
const browser = await chromium.launch({ channel: process.env.E2E_CHANNEL || 'msedge' })
try {
  for (const [name, width, height] of [['desktop', 1440, 1000], ['mobile', 390, 844]]) {
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1, reducedMotion: 'reduce' })
    const failures = []
    page.on('pageerror', error => failures.push(error.message))
    await page.goto('http://127.0.0.1:3000/')
    await page.evaluate(() => document.fonts.ready)
    const total = await page.evaluate(() => document.documentElement.scrollHeight)
    for (let y = 0; y < total; y += 700) {
      await page.evaluate(y => window.scrollTo(0, y), y)
      await page.waitForTimeout(60)
    }
    await page.evaluate(async () => {
      await Promise.all(Array.from(document.images).map(image => image.decode().catch(() => {})))
      window.scrollTo(0, 0)
    })
    await page.screenshot({ path: `${output}/${name}.png`, fullPage: true })
    await page.screenshot({ path: `${output}/${name}-hero.png` })
    await page.locator('#request').scrollIntoViewIfNeeded()
    await page.screenshot({ path: `${output}/${name}-form.png` })
    console.log(JSON.stringify({
      name,
      headers: await page.locator('.site-header').count(),
      hero: await page.locator('h1').count(),
      form: await page.locator('.request-panel').count(),
      overflow: await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1),
      failures,
    }))
    await page.close()
  }
} finally { await browser.close() }
