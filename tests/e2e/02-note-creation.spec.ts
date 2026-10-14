import { test, expect, type Page } from '@playwright/test'

const ADMIN_USERNAME = process.env.E2E_ADMIN_USERNAME ?? 'ci-admin'
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD ?? 'ci-test-admin-password'

async function login(page: Page) {
  await page.goto('/manage')
  await expect(page.locator('#username')).toBeVisible()
  await page.locator('#username').fill(ADMIN_USERNAME)
  await page.locator('#password').fill(ADMIN_PASSWORD)
  await page.getByRole('button', { name: '密码登录', exact: true }).click()
  await expect(page.getByRole('heading', { name: '管理面板', exact: true })).toBeVisible({ timeout: 15_000 })
}

// Uniqueness notes:
// - #content-title / '从这里开始写作...' placeholder: single inputs in ContentEditor.
// - '保存草稿' button: exact:true; the only such button (ContentEditor actions).
// - '已保存' is scoped inside [data-content-editor] with exact:true, so it cannot collide with
//   unrelated "已保存"/"设置已保存" text elsewhere in the app.
test('E2E-02: 新建笔记并保存后可再次编辑保存', async ({ page }) => {
  await login(page)
  await page.goto('/manage/notes/new')

  const editor = page.locator('[data-content-editor]')
  const saveButton = page.getByRole('button', { name: '保存草稿', exact: true })
  const savedIndicator = editor.getByText('已保存', { exact: true })

  const title = `E2E 笔记 ${Date.now()}`
  await page.locator('#content-title').fill(title)
  await page.getByPlaceholder('从这里开始写作...').fill('E2E 自动化测试内容。')
  await saveButton.click()

  await expect(savedIndicator).toBeVisible({ timeout: 15_000 })
  await expect(page).toHaveURL(/\/manage\/notes\/.+/)

  await page.locator('#content-title').fill(`${title} 已编辑`)
  await saveButton.click()
  await expect(savedIndicator).toBeVisible({ timeout: 15_000 })
})
