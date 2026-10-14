import { apiFetch } from './client'

export type AttemptContextType = 'practice' | 'review' | 'editor_check'

export interface Attempt {
  id: string
  question_id: string
  submitted_answer: string
  is_correct: boolean
  context_type: AttemptContextType
  mistake_draft_item_id: string | null
  submitted_at: string
}

export function submitAttempt(question_id: string, submitted_answer: string): Promise<Attempt> {
  return apiFetch<Attempt>('/api/admin/attempts', {
    method: 'POST',
    body: JSON.stringify({ question_id, submitted_answer }),
  })
}

export type ReanswerVerdict = 'correct' | 'incorrect' | 'needs_human'

export interface ReanswerEvaluation {
  verdict: ReanswerVerdict
  recommendation: number | null
}

export interface ReanswerResult {
  attempt: Attempt
  evaluation: ReanswerEvaluation
}

export function submitReanswer(question_id: string, submitted_answer: string): Promise<ReanswerResult> {
  return apiFetch<ReanswerResult>('/api/admin/attempts/review', {
    method: 'POST',
    body: JSON.stringify({ question_id, submitted_answer }),
  })
}
