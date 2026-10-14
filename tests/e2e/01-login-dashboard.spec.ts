import { test, expect, type Page } from '@playwright/test'

const ADMIN_USERNAME = process.env.E2E_ADMIN_USERNAME ?? 'ci-admin'
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD ?? 'ci-test-admin-password'

// Uniqueness notes:
// - #username / #password: the only two inputs on the login form (src/app/manage/page.tsx).
// - '密码登录' button: matched with exact:true; the only other occurrences of that text on the
//   page are paragraphs (passkey hint), not buttons.
// - '管理面板' heading: exact:true; the body copy at src/app/manage/page.tsx:688 also contains
//   the substring "管理面板", so substring matching would be ambiguous.
// - '学习管理首页' heading: exact:true avoids the "学习管理首页加载失败" error title in
//   dashboard/error.tsx.
// - '快速开始' heading: the only occurrence is the dashboard QuickActionsSection h2.
async function login(page: Page) {
  await page.goto('/manage')
  await expect(page.locator('#username')).toBeVisible()
  await page.locator('#username').fill(ADMIN_USERNAME)
  await page.locator('#password').fill(ADMIN_PASSWORD)
  await page.getByRole('button', { name: '密码登录', exact: true }).click()
  await expect(page.getByRole('heading', { name: '管理面板', exact: true })).toBeVisible({ timeout: 15_000 })
}

test('E2E-01: 未登录访问工作区跳转登录，登录后进入学习管理首页', async ({ page }) => {
  await page.goto('/manage/dashboard')
  await expect(page).toHaveURL(/\/manage(\?|$)/)
  await expect(page.locator('#username')).toBeVisible()

  await login(page)
  await page.goto('/manage/dashboard')
  await expect(page.getByRole('heading', { name: '学习管理首页', exact: true })).toBeVisible({ timeout: 15_000 })
  await expect(page.getByRole('heading', { name: '快速开始', exact: true })).toBeVisible()
})
