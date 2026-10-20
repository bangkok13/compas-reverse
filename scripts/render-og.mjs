import { chromium } from '../frontend/node_modules/playwright/index.mjs'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
const browser = await chromium.launch({ channel: process.env.E2E_CHANNEL || 'msedge' })
try {
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 })
  await page.goto(pathToFileURL(resolve('frontend/public/og-image.svg')).href)
  await page.screenshot({ path: resolve('frontend/public/og-image.png'), omitBackground: false })
} finally { await browser.close() }
