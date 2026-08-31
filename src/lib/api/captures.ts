import { apiFetch } from './client'
import type { Difficulty, QuestionType } from './questions'
import type { MistakeReason } from './mistakes'

export type CaptureStatus =
  | 'uploaded'
  | 'recognizing'
  | 'recognized'
  | 'drafting'
  | 'ready'
  | 'failed'
  | 'converted'
  | 'archived'

export type CaptureLastStage = 'recognize' | 'draft' | 'convert'

export interface KnowledgePointSuggestion {
  id: number | null
  label: string
  confidence: number | null
}

export interface SubjectSuggestion {
  id: number | null
  label: string | null
  confidence: number | null
}

export interface Capture {
  id: string
  source_attachment_id: string
  status: CaptureStatus
  recognized_text: string | null
  user_error_context: string | null
  question_draft_text: string | null
  analysis_draft_text: string | null
  error_summary_draft: string | null
  subject_id: number | null
  knowledge_point_suggestions: KnowledgePointSuggestion[]
  model_output_version: string
  attempt_count: number
  last_stage: CaptureLastStage | null
  error_code: string | null
  error_message_safe: string | null
  started_at: string | null
  finished_at: string | null
  mistake_draft_item_id: string | null
  created_by: string | null
  created_at: string
  updated_at: string
}

export interface CaptureCreate {
  attachment_id: string
}

export interface CapturePatch {
  recognized_text?: string | null
  user_error_context?: string | null
  question_draft_text?: string | null
  analysis_draft_text?: string | null
  error_summary_draft?: string | null
  subject_id?: number | null
  knowledge_point_suggestions?: KnowledgePointSuggestion[] | null
}

export interface CaptureConvert {
  subject_id: number
  question_text: string
  question_type: QuestionType
  options?: string[]
  correct_answer?: string | null
  explanation?: string | null
  difficulty?: Difficulty | null
  my_answer?: string | null
  reason_category?: MistakeReason
  mistake_reason?: string | null
  knowledge_point_ids?: number[]
}

export interface ConvertResult {
  capture: Capture
  mistake_draft_item_id: string
  question_draft_id: string | null
}

function queryString(filters: Record<string, string | undefined>): string {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined) params.set(key, value)
  })
  const query = params.toString()
  return query ? `?${query}` : ''
}

export function listCaptures(status?: CaptureStatus): Promise<Capture[]> {
  return apiFetch<Capture[]>(`/api/admin/captures${queryString({ status })}`)
}

export function createCapture(attachmentId: string): Promise<Capture> {
  return apiFetch<Capture>('/api/admin/captures', {
    method: 'POST',
    body: JSON.stringify({ attachment_id: attachmentId }),
  })
}

export function getCapture(id: string): Promise<Capture> {
  return apiFetch<Capture>(`/api/admin/captures/${id}`)
}

export function patchCapture(id: string, patch: CapturePatch): Promise<Capture> {
  return apiFetch<Capture>(`/api/admin/captures/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(patch),
  })
}

export function triggerRecognition(id: string): Promise<Capture> {
  return apiFetch<Capture>(`/api/admin/captures/${id}/recognize`, {
    method: 'POST',
  })
}

export function triggerDraft(id: string): Promise<Capture> {
  return apiFetch<Capture>(`/api/admin/captures/${id}/draft`, {
    method: 'POST',
  })
}

export function convertCapture(
  id: string,
  payload: CaptureConvert,
): Promise<ConvertResult> {
  return apiFetch<ConvertResult>(`/api/admin/captures/${id}/convert`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
