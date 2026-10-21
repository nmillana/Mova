import { chromium, expect } from '@playwright/test';

const browser = await chromium.launch({ channel: 'msedge', headless: true });
const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
const problems = [];
page.on('pageerror', error => problems.push(error.message));
page.on('console', message => message.type() === 'error' && problems.push(message.text()));

await page.goto('http://127.0.0.1:5178/');
await page.evaluate(() => localStorage.setItem('mova-personal-v1', JSON.stringify({
  version: 1,
  profile: { name: '', goal: 'habit', level: 'new', minutes: 10, days: 3, equipment: [], avoid: [], sound: false },
  sessions: [],
  active: null
})));
await page.reload();
await page.getByRole('button', { name: 'Vamos a movernos' }).click();
await page.getByRole('button', { name: 'Estoy listo', exact: true }).click();
await expect(page.getByRole('heading', { name: 'Marcha suave' })).toBeVisible();
await page.screenshot({ path: 'artifacts/personaje-corregido.png', fullPage: true });
expect(problems).toEqual([]);
console.log(JSON.stringify({ figureVisible: true, consoleErrors: problems }));
await browser.close();
