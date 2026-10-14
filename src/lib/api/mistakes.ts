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
export type MistakeVisibility = 'private' | 'public'

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
  visibility: MistakeVisibility
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
  /**
   * B05b: the retired optional binding. The backend rejects this field; only
   * the canonical `confirmMistakeAiCandidate` flow binds a run to a draft.
   */
  source_run_id?: string
}

export interface MistakeAiCandidate {
  run_id: string
  review_revision: number
  candidate: Record<string, unknown>
}

export interface MistakeAiCandidateInput {
  question_id: string
  my_answer: string | null
  user_error_reason: string
}

export interface MistakeAiConfirmInput {
  run_id: string
  review_revision: number
  question_id: string
  my_answer: string | null
  user_error_reason: string | null
  reason_category: MistakeReason
  mistake_reason: string | null
  difficulty: Difficulty | null
  knowledge_point_ids: number[]
  confirmed_candidate: Record<string, unknown>
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

export function createMistakeAiCandidate(
  input: MistakeAiCandidateInput,
): Promise<MistakeAiCandidate> {
  return apiFetch<MistakeAiCandidate>('/api/admin/mistakes/ai-candidate', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function confirmMistakeAiCandidate(
  input: MistakeAiConfirmInput,
): Promise<MistakeDraft> {
  return apiFetch<MistakeDraft>('/api/admin/mistakes/ai-confirm', {
    method: 'POST',
    body: JSON.stringify(input),
  })
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

export interface MistakeVisibilityUpdate {
  visibility: MistakeVisibility
  version: number
}

export function updateMistakeVisibility(
  id: string,
  input: MistakeVisibilityUpdate,
): Promise<Mistake> {
  return apiFetch<Mistake>(`/api/admin/mistakes/${id}/visibility`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  })
}

export interface PublicMistake {
  id: string
  title: string | null
  question_text: string
  correct_answer: string | null
  analysis: string | null
  reason_category: MistakeReason
  mistake_reason: string | null
  difficulty: Exclude<Difficulty, 'unspecified'> | null
  knowledge_point_ids: number[]
  created_at: string
  updated_at: string
}

export interface PublicMistakeListResponse {
  items: PublicMistake[]
  total: number
  page: number
  size: number
  empty: boolean
  message: string | null
}

export function listPublicMistakes(
  params?: { page?: number; size?: number },
): Promise<PublicMistakeListResponse> {
  const searchParams = new URLSearchParams()
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.size) searchParams.set('size', String(params.size))
  const qs = searchParams.toString()
  return apiFetch<PublicMistakeListResponse>(
    `/api/public/mistakes${qs ? `?${qs}` : ''}`,
  )
}
