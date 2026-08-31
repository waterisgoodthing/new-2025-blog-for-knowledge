import { apiFetch } from './client'
import type { Difficulty } from './questions'

export type MistakeReason =
  | 'concept'
  | 'calculation'
  | 'reading'
  | 'careless'
  | 'unknown'
export type MistakeDraftStatus = 'pending' | 'needs_fix' | 'rejected' | 'converted'
export type MistakeStatus = 'active' | 'archived'

export interface MistakeDraft {
  id: string
  draft_item_id: string
  question_id: string | null
  question_draft_id: string | null
  subject_id: number
  title: string | null
  question_text: string
  my_answer: string | null
  correct_answer_snapshot: string | null
  explanation_snapshot: string | null
  reason_category: MistakeReason
  mistake_reason: string | null
  difficulty: Difficulty | null
  knowledge_point_ids: number[]
  status: MistakeDraftStatus
  version: number
  target_id: string | null
  created_at: string
  updated_at: string
}

export interface Mistake {
  id: string
  source_draft_item_id: string
  question_id: string
  subject_id: number
  title: string | null
  question_text: string
  my_answer: string | null
  correct_answer: string | null
  analysis: string | null
  reason_category: MistakeReason
  mistake_reason: string | null
  difficulty: Difficulty | null
  status: MistakeStatus
  visibility: 'private'
  version: number
  knowledge_point_ids: number[]
  review_item_id: string
  created_at: string
  updated_at: string
}

export interface MistakeDraftCreate {
  question_id?: string
  question_draft_id?: string
  my_answer?: string | null
  reason_category?: MistakeReason
  mistake_reason?: string | null
  difficulty?: Difficulty | null
  knowledge_point_ids?: number[]
}

export interface MistakeDraftUpdate {
  version: number
  my_answer?: string | null
  reason_category?: MistakeReason
  mistake_reason?: string | null
  difficulty?: Difficulty | null
  knowledge_point_ids?: number[]
}

export interface MistakeUpdate {
  version: number
  my_answer?: string | null
  analysis?: string | null
  reason_category?: MistakeReason
  mistake_reason?: string | null
  difficulty?: Difficulty | null
  knowledge_point_ids?: number[]
}

export function listMistakeDrafts(
  status?: MistakeDraftStatus,
): Promise<MistakeDraft[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : ''
  return apiFetch<MistakeDraft[]>(`/api/admin/mistake-drafts${query}`)
}

export function createMistakeDraft(
  input: MistakeDraftCreate,
): Promise<MistakeDraft> {
  return apiFetch<MistakeDraft>('/api/admin/mistake-drafts', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function getMistakeDraft(id: string): Promise<MistakeDraft> {
  return apiFetch<MistakeDraft>(`/api/admin/mistake-drafts/${id}`)
}

export function updateMistakeDraft(
  id: string,
  input: MistakeDraftUpdate,
): Promise<MistakeDraft> {
  return apiFetch<MistakeDraft>(`/api/admin/mistake-drafts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export function rejectMistakeDraft(
  id: string,
  version: number,
): Promise<MistakeDraft> {
  return apiFetch<MistakeDraft>(`/api/admin/mistake-drafts/${id}/reject`, {
    method: 'POST',
    body: JSON.stringify({ version }),
  })
}

export function convertMistakeDraft(
  id: string,
  version: number,
): Promise<Mistake> {
  return apiFetch<Mistake>(`/api/admin/mistake-drafts/${id}/convert`, {
    method: 'POST',
    body: JSON.stringify({ version }),
  })
}

export function listMistakes(status?: MistakeStatus): Promise<Mistake[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : ''
  return apiFetch<Mistake[]>(`/api/admin/mistakes${query}`)
}

export function getMistake(id: string): Promise<Mistake> {
  return apiFetch<Mistake>(`/api/admin/mistakes/${id}`)
}

export function updateMistake(
  id: string,
  input: MistakeUpdate,
): Promise<Mistake> {
  return apiFetch<Mistake>(`/api/admin/mistakes/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export function archiveMistake(id: string, version: number): Promise<Mistake> {
  return apiFetch<Mistake>(`/api/admin/mistakes/${id}`, {
    method: 'DELETE',
    body: JSON.stringify({ version }),
  })
}
