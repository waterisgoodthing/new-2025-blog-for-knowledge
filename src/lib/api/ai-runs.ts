import { apiFetch } from './client'

export type AiRunStatus = 'running' | 'succeeded' | 'failed'
export type AiRunValidationStatus = 'pending' | 'passed' | 'failed' | 'warning' | 'not_applicable'
export type AiRunReviewStatus = 'not_required' | 'pending' | 'accepted' | 'rejected'

export interface AiRunListItem {
  id: string
  task_type: string
  target_type: string | null
  target_id: string | null
  provider_used: string | null
  model: string | null
  prompt_version: string | null
  status: AiRunStatus
  validation_status: AiRunValidationStatus
  review_status: AiRunReviewStatus
  review_revision: number
  attempt: number
  parent_run_id: string | null
  latency_ms: number | null
  error_code: string | null
  error_message_safe: string | null
  started_at: string
  finished_at: string | null
  created_at: string
  updated_at: string
}

export interface AiRunDetail extends AiRunListItem {
  output_data: Record<string, unknown> | unknown[] | string | null
  warnings: unknown[] | null
  reviewed_at: string | null
  review_note: string | null
}

export interface AiRunListResponse {
  items: AiRunListItem[]
  total: number
  limit: number
  offset: number
}

export async function getAiRuns(params?: {
  task_type?: string
  status?: AiRunStatus | ''
  validation_status?: AiRunValidationStatus | ''
  review_status?: AiRunReviewStatus | ''
  limit?: number
  offset?: number
}): Promise<AiRunListResponse> {
  const query = new URLSearchParams()
  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== '') query.set(key, String(value))
  })
  const suffix = query.toString()
  return apiFetch<AiRunListResponse>(`/api/admin/ai/runs${suffix ? `?${suffix}` : ''}`)
}

export async function getAiRun(runId: string): Promise<AiRunDetail> {
  return apiFetch<AiRunDetail>(`/api/admin/ai/runs/${runId}`)
}

export async function retryAiRun(runId: string): Promise<AiRunDetail> {
  return apiFetch<AiRunDetail>(`/api/admin/ai/runs/${runId}/retry`, {
    method: 'POST',
    body: JSON.stringify({}),
  })
}

export async function decideAiRun(
  runId: string,
  decision: 'accepted' | 'rejected',
  expectedRevision: number,
  note?: string,
): Promise<AiRunDetail> {
  return apiFetch<AiRunDetail>(`/api/admin/ai/runs/${runId}/decision`, {
    method: 'POST',
    body: JSON.stringify({
      decision,
      expected_revision: expectedRevision,
      note: note || null,
    }),
  })
}
