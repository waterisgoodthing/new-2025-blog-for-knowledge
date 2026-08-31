import { apiFetch } from './client'

export interface DashboardSummary {
  generated_at: string
  counts: {
    questions: number
    mistakes: number
    knowledge_points: number
    attachments: number
    due_reviews: number
  }
  recent_questions: Array<{
    id: string
    title: string | null
    question_text: string
    updated_at: string
  }>
  recent_mistakes: Array<{
    id: string
    title: string | null
    question_text: string
    reason_category: string
    updated_at: string
  }>
  recent_reviews: Array<{
    id: string
    review_item_id: string
    rating: number
    reviewed_at: string
    question_text: string
  }>
  sections: {
    learning: 'ready' | 'unavailable' | 'empty'
    activity: 'ready' | 'unavailable' | 'empty'
    storage: 'ready' | 'unknown' | 'empty'
  }
  system: {
    service: 'ok'
    database: 'ok' | 'unavailable'
    storage: 'ok' | 'unknown'
  }
}

export function getDashboardSummary(): Promise<DashboardSummary> {
  return apiFetch<DashboardSummary>('/api/admin/dashboard/summary')
}
