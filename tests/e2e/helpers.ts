import { expect, type Page } from '@playwright/test'

export const ADMIN_USERNAME = process.env.E2E_ADMIN_USERNAME ?? 'ci-admin'
export const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD ?? 'ci-test-admin-password'

// The API origin the built frontend calls. Defaults to the CI topology
// (api.ci.test:8001); local same-site runs override E2E_API_URL.
export const API_BASE = (process.env.E2E_API_URL ?? 'http://api.ci.test:8001').replace(/\/$/, '')

export const SEED_QUESTION_TITLE = process.env.E2E_SEED_QUESTION_TITLE ?? 'E2E-W4-BUSINESS-Q'
export const SEED_QUESTION_TEXT =
  process.env.E2E_SEED_QUESTION_TEXT ??
  'E2E-W4-REVIEW-Q 固定间隔复习 v2：连续成功第 1 次应推进到几天？'
export const SEED_CORRECT_ANSWER = process.env.E2E_SEED_CORRECT_ANSWER ?? '3'

export async function login(page: Page): Promise<void> {
  await page.goto('/manage')
  await expect(page.locator('#username')).toBeVisible()
  await page.locator('#username').fill(ADMIN_USERNAME)
  await page.locator('#password').fill(ADMIN_PASSWORD)
  await page.getByRole('button', { name: '密码登录', exact: true }).click()
  await expect(page.getByRole('heading', { name: '管理面板', exact: true })).toBeVisible({
    timeout: 15_000,
  })
}

/**
 * Session-authenticated backend read performed *inside the page*.
 *
 * It must run in the browser, not via the Node-side APIRequestContext: only the
 * browser honors `--host-resolver-rules` (local same-site runs) and it already
 * holds the `admin_session` cookie for the API origin. `credentials:'include'`
 * matches the app's own client and the backend CORS allows the page origin.
 */
export async function apiGet<T>(page: Page, path: string): Promise<T> {
  const result = await page.evaluate(async (url) => {
    const response = await fetch(url, { credentials: 'include' })
    return { ok: response.ok, status: response.status, text: await response.text() }
  }, `${API_BASE}${path}`)
  expect(result.ok, `GET ${path} -> HTTP ${result.status}`).toBeTruthy()
  return JSON.parse(result.text) as T
}

export interface SeedQuestion {
  id: string
  subject_id: number
  title: string | null
  question_text: string
  question_type: string
  answer_data: { kind: string; value: unknown }
  status: string
}

export async function findSeedQuestion(page: Page): Promise<SeedQuestion> {
  const questions = await apiGet<SeedQuestion[]>(page, '/api/admin/questions?status=active')
  const question = questions.find((candidate) => candidate.title === SEED_QUESTION_TITLE)
  expect(question, `seed question "${SEED_QUESTION_TITLE}" must exist`).toBeTruthy()
  return question as SeedQuestion
}

export interface SeedReviewItem {
  id: string
  target_id: string
  state: string
  next_review_at: string
  question_text: string
}

export async function findSeedReviewItem(page: Page): Promise<SeedReviewItem> {
  const items = await apiGet<SeedReviewItem[]>(page, '/api/admin/review/items?due=true')
  const item = items.find((candidate) => candidate.question_text === SEED_QUESTION_TEXT)
  expect(item, 'seeded due review item must be in the due queue').toBeTruthy()
  return item as SeedReviewItem
}

export interface SeedMistakeDraft {
  draft_item_id: string
  question_id: string | null
  attempt_id: string | null
  question_text: string
  my_answer: string | null
  status: string
}

export async function listMistakeDrafts(page: Page): Promise<SeedMistakeDraft[]> {
  return apiGet<SeedMistakeDraft[]>(page, '/api/admin/mistake-drafts')
}

export interface SeedReviewRecord {
  id: string
  review_item_id: string
  rating: number
  attempt_id: string | null
  new_state: string
  reviewed_at: string
}

export async function listReviewRecords(
  page: Page,
  itemId: string,
): Promise<SeedReviewRecord[]> {
  return apiGet<SeedReviewRecord[]>(page, `/api/admin/review/items/${itemId}/records`)
}
