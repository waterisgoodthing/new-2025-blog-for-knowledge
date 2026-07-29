import { apiFetch } from './client'

export type ReviewRating = 0 | 1 | 2 | 3 | 4 | 5

export interface ReviewItem {
  id: string
  target_type: 'mistake'
  target_id: string
  state: 'active' | 'paused'
  algorithm: 'fixed_interval_v1'
  interval_days: number
  repetitions: number
  next_review_at: string
  last_reviewed_at: string | null
  question_text: string
  mistake_reason: string | null
}

export interface ReviewRecord {
  id: string
  review_item_id: string
  rating: ReviewRating
  reviewed_at: string
  previous_interval_days: number
  next_interval_days: number
  previous_next_review_at: string
  next_review_at: string
  created_at: string
}

export function listDueReviewItems(): Promise<ReviewItem[]> {
  return apiFetch<ReviewItem[]>('/api/admin/review/items?due=true')
}

export function listReviewRecords(itemId: string): Promise<ReviewRecord[]> {
  return apiFetch<ReviewRecord[]>(
    `/api/admin/review/items/${itemId}/records`,
  )
}

export function submitReview(
  itemId: string,
  rating: ReviewRating,
  expectedNextReviewAt: string,
): Promise<ReviewItem> {
  return apiFetch<ReviewItem>(`/api/admin/review/items/${itemId}/submit`, {
    method: 'POST',
    body: JSON.stringify({
      rating,
      expected_next_review_at: expectedNextReviewAt,
    }),
  })
}
