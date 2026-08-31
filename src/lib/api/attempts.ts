import { apiFetch } from './client'

export interface Attempt {
  id: string
  question_id: string
  submitted_answer: string
  is_correct: boolean
  mistake_draft_item_id: string | null
  submitted_at: string
}

export function submitAttempt(question_id: string, submitted_answer: string): Promise<Attempt> {
  return apiFetch<Attempt>('/api/admin/attempts', {
    method: 'POST',
    body: JSON.stringify({ question_id, submitted_answer }),
  })
}
