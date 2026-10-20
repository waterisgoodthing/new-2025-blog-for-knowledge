import { test, expect } from '@playwright/test'

import {
  SEED_CORRECT_ANSWER,
  findSeedReviewItem,
  listReviewRecords,
  login,
} from './helpers'

// R22b E2E-04 — mistake → review → re-answer → review record.
//
// Real path (src/app/manage/(workspace)/review/review-queue.tsx):
//   due ReviewItem card → 再答 → submit answer → backend judges it via
//   /api/admin/attempts/review (creates a review-context Attempt) → click the
//   recommended six-band rating → /api/admin/review/items/<id>/submit creates a
//   ReviewRecord carrying that attempt_id.
//
// Strict-mode-safe locators:
// - The seeded item is located by its exact question_text h3, then scoped to the
//   nearest ManagePanel card (`div.rounded-lg`), so ratings/buttons from other
//   due items cannot collide.
// - The six-band rating is addressed by its unique aria-label regex for rating 4.
test('E2E-04: 复习再答并写入 ReviewRecord（真实页面操作 + 后端读回）', async ({
  page,
}) => {
  await login(page)

  const item = await findSeedReviewItem(page)

  await page.goto('/manage/review')
  await expect(page.getByRole('heading', { name: '复习', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { name: '今日到期', exact: true })).toBeVisible()

  const card = page
    .getByRole('heading', { name: item.question_text, exact: true })
    .locator('xpath=ancestor::div[contains(@class,"rounded-lg")][1]')
  await expect(card).toBeVisible({ timeout: 15_000 })

  // --- Re-answer: judged attempt, context_type='review', no new drafts. ---
  await card.getByRole('button', { name: '再答', exact: true }).click()
  const answerInput = card.getByPlaceholder('输入本次重做答案')
  await expect(answerInput).toBeVisible({ timeout: 15_000 })
  await answerInput.fill(SEED_CORRECT_ANSWER)

  const reanswerPromise = page.waitForResponse(
    (response) =>
      response.url().endsWith('/api/admin/attempts/review') &&
      response.request().method() === 'POST',
  )
  await card.getByRole('button', { name: '提交作答', exact: true }).click()
  const reanswerResponse = await reanswerPromise
  expect(reanswerResponse.status()).toBe(201)

  const reanswer = (await reanswerResponse.json()) as {
    attempt: { id: string; question_id: string; context_type: string; is_correct: boolean }
    evaluation: { verdict: string; recommendation: number | null }
  }
  expect(reanswer.attempt.context_type).toBe('review')
  expect(reanswer.attempt.is_correct).toBe(true)
  expect(reanswer.evaluation.verdict).toBe('correct')
  expect(reanswer.evaluation.recommendation).toBe(4)

  // The evaluated verdict pre-selects the recommended rating.
  const ratingButton = card.getByRole('button', { name: /提交 4 分复习结果/ })
  await expect(ratingButton).toBeVisible({ timeout: 15_000 })

  const submitPromise = page.waitForResponse(
    (response) =>
      /\/api\/admin\/review\/items\/.+\/submit$/.test(response.url()) &&
      response.request().method() === 'POST',
  )
  await ratingButton.click()
  const submitResponse = await submitPromise
  expect(submitResponse.status()).toBe(200)

  await expect(page.getByText(/已提交复习/)).toBeVisible({ timeout: 15_000 })

  // Backend readback: a ReviewRecord exists for this item, with the chosen
  // rating and the exact review-context Attempt id captured above.
  const records = await listReviewRecords(page, item.id)
  expect(records.length).toBeGreaterThan(0)
  const newest = records[0]
  expect(newest.review_item_id).toBe(item.id)
  expect(newest.rating).toBe(4)
  expect(newest.attempt_id).toBe(reanswer.attempt.id)
})
