import { test, expect } from '@playwright/test'

import { findSeedQuestion, listMistakeDrafts, login } from './helpers'

// R22b E2E-03 — question → wrong attempt → mistake draft.
//
// Real path (src/app/manage/(workspace)/questions/components/question-editor.tsx):
//   open a seeded active Question → 作答验证 → submit a wrong answer →
//   backend creates an Attempt and (because is_correct=false) a pending
//   MistakeDraft, and the UI navigates to /manage/mistakes/<draft>?kind=draft.
//
// Strict-mode-safe locators:
// - `section` scoped by the '作答验证' h2 holds exactly one textarea (the answer box)
//   and the single '提交作答' button; substring matches elsewhere on the page are excluded.
test('E2E-03: 错误作答生成待确认错题草稿（真实页面操作 + 后端读回）', async ({
  page,
}) => {
  await login(page)

  const question = await findSeedQuestion(page)

  await page.goto(`/manage/questions/${question.id}`)
  await expect(page.getByRole('heading', { name: '编辑正式题目', exact: true })).toBeVisible()

  const attemptSection = page
    .getByRole('heading', { name: '作答验证', exact: true })
    .locator('xpath=ancestor::section[1]')
  await expect(attemptSection).toBeVisible()
  const answerBox = attemptSection.getByRole('textbox')
  await expect(answerBox).toHaveCount(1)

  const wrongAnswer = `E2E-WRONG-${Date.now()}`
  await answerBox.fill(wrongAnswer)

  const attemptResponsePromise = page.waitForResponse(
    (response) =>
      response.url().endsWith('/api/admin/attempts') &&
      response.request().method() === 'POST',
  )
  await attemptSection.getByRole('button', { name: '提交作答', exact: true }).click()
  const attemptResponse = await attemptResponsePromise
  expect(attemptResponse.status()).toBe(201)

  const attempt = (await attemptResponse.json()) as {
    id: string
    question_id: string
    submitted_answer: string
    is_correct: boolean
    context_type: string
    mistake_draft_item_id: string | null
  }

  // Business outcome part 1: the wrong answer is a private, non-review attempt.
  expect(attempt.is_correct).toBe(false)
  expect(attempt.context_type).toBe('practice')
  expect(attempt.question_id).toBe(question.id)
  expect(attempt.submitted_answer).toBe(wrongAnswer)
  expect(attempt.mistake_draft_item_id).toBeTruthy()
  const draftId = attempt.mistake_draft_item_id as string

  // The UI takes the wrong-answer branch into the pending draft.
  await expect(page).toHaveURL(new RegExp(`/manage/mistakes/${draftId}\\?kind=draft`))

  // Business outcome part 2: backend readback proves the draft is persisted,
  // pending, linked to this attempt and to the seeded question.
  const drafts = await listMistakeDrafts(page)
  const draft = drafts.find((candidate) => candidate.draft_item_id === draftId)
  expect(draft, 'backend readback must find the created mistake draft').toBeTruthy()
  expect(draft?.attempt_id).toBe(attempt.id)
  expect(draft?.question_id).toBe(question.id)
  expect(draft?.status).toBe('pending')
  expect(draft?.question_text).toBe(question.question_text)
  expect(draft?.my_answer).toBe(wrongAnswer)
})
