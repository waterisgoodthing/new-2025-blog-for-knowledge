import { apiFetch } from './client'
import type {
  Difficulty,
  Question,
  QuestionType,
} from './questions'

export type DraftStatus = 'pending' | 'needs_fix' | 'rejected' | 'converted'

export interface DraftItem {
  id: string
  draft_type: 'question'
  source_type: 'manual'
  source_id: string | null
  status: DraftStatus
  version: number
  validation_errors: Array<Record<string, unknown>>
  target_type: 'question' | null
  target_id: string | null
  created_at: string
  updated_at: string
}

export interface QuestionDraft {
  id: string
  draft_item_id: string
  subject_id: number
  title: string | null
  question_text: string
  question_type: QuestionType
  options: string[]
  correct_answer: string | null
  explanation: string | null
  difficulty: Difficulty | null
  knowledge_point_ids: number[]
  item: DraftItem
  created_at: string
  updated_at: string
}

export interface QuestionDraftCreate {
  subject_id: number
  title?: string | null
  question_text: string
  question_type: QuestionType
  options?: string[]
  correct_answer?: string | null
  explanation?: string | null
  difficulty?: Difficulty | null
  knowledge_point_ids?: number[]
}

export interface QuestionDraftUpdate {
  version: number
  subject_id?: number
  title?: string | null
  question_text?: string
  question_type?: QuestionType
  options?: string[]
  correct_answer?: string | null
  explanation?: string | null
  difficulty?: Difficulty | null
  knowledge_point_ids?: number[]
}

export function listDrafts(status?: DraftStatus): Promise<QuestionDraft[]> {
  const params = new URLSearchParams({ draft_type: 'question' })
  if (status) params.set('status', status)
  return apiFetch<QuestionDraft[]>(`/api/admin/drafts?${params.toString()}`)
}

export function createQuestionDraft(
  input: QuestionDraftCreate,
): Promise<QuestionDraft> {
  return apiFetch<QuestionDraft>('/api/admin/drafts/questions', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function getQuestionDraft(id: string): Promise<QuestionDraft> {
  return apiFetch<QuestionDraft>(`/api/admin/drafts/${id}`)
}

export function updateQuestionDraft(
  id: string,
  input: QuestionDraftUpdate,
): Promise<QuestionDraft> {
  return apiFetch<QuestionDraft>(`/api/admin/drafts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export function rejectQuestionDraft(
  id: string,
  version: number,
): Promise<QuestionDraft> {
  return apiFetch<QuestionDraft>(`/api/admin/drafts/${id}/reject`, {
    method: 'POST',
    body: JSON.stringify({ version }),
  })
}

export function convertQuestionDraft(
  id: string,
  version: number,
): Promise<Question> {
  return apiFetch<Question>(`/api/admin/drafts/${id}/convert`, {
    method: 'POST',
    body: JSON.stringify({ version }),
  })
}
