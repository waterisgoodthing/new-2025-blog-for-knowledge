import { test, expect } from '@playwright/test'

// Uniqueness notes:
// - main[data-render-state] is the single NotesPage <main> (src/app/notes/page.tsx:199).
// - '加载失败' heading exact:true is the AsyncStatePanel error title; the notes route does not
//   render the EmptyState '加载失败' variant in this state.
// - '重试' button exact:true is the single AsyncStatePanel retry control.
test('E2E-05: 公开笔记页 API 失败时显示错误状态，重试后恢复', async ({ page }) => {
  await page.route('**/api/notes*', (route) =>
    route.fulfill({
      status: 503,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Service unavailable' }),
    }),
  )

  await page.goto('/notes')

  const renderRoot = page.locator('main[data-render-state]')
  await expect(renderRoot).toHaveAttribute('data-render-state', 'error', { timeout: 15_000 })
  await expect(page.getByRole('heading', { name: '加载失败', exact: true })).toBeVisible()
  const retryButton = page.getByRole('button', { name: '重试', exact: true })
  await expect(retryButton).toBeVisible()

  await page.unroute('**/api/notes*')
  await retryButton.click()
  await expect(renderRoot).toHaveAttribute('data-render-state', /ready|empty/, { timeout: 15_000 })
  await expect(page.getByRole('heading', { name: '加载失败', exact: true })).toHaveCount(0)
})
