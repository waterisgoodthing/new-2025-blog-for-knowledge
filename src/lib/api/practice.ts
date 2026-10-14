import { apiFetch } from './client'

export interface PracticeItem {
  question_id: string
  knowledge_point_id: number
  selection_reason: string
}

export interface PracticeEmptyMetadata {
  reason: string
  raw_candidate_count: number
  recent_attempt_excluded_count: number
  mastered_excluded_count: number
  eligible_candidate_count: number
  target_count: number
  returned_count: number
  window_hours: number
}

export interface PracticeTodayResponse {
  items: PracticeItem[]
  empty_metadata: PracticeEmptyMetadata
}

export function getTodayPractice(): Promise<PracticeTodayResponse> {
  return apiFetch<PracticeTodayResponse>('/api/admin/practice/today')
}
