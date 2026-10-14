import { apiFetch } from './client'

export interface DashboardWeakKnowledgePoint {
  knowledge_point_id: number
  name: string
  attempt_count: number
  wrong_rate: number
  lapse_count: number
  due_count: number
}

export interface DashboardRecentlyMasteredItem {
  review_item_id: string
  mistake_id: string
  question_text: string
  mastered_at: string
}

export interface DashboardSectionAction {
  section: 'review' | 'practice'
  count: number
  available: boolean
  target_route: string
  reason: string
}

export interface DashboardSectionActions {
  review: DashboardSectionAction
  practice: DashboardSectionAction
}

export interface DashboardTodayFirstAction {
  kind: 'review' | 'practice' | 'none'
  count: number
  target_route: string | null
  reason: string
}

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
  review_today_count: number
  practice_today_count: number
  weak_top3: DashboardWeakKnowledgePoint[]
  recently_mastered_4: DashboardRecentlyMasteredItem[]
  today_first_action: DashboardTodayFirstAction
  section_actions: DashboardSectionActions
}

export function getDashboardSummary(): Promise<DashboardSummary> {
  return apiFetch<DashboardSummary>('/api/admin/dashboard/summary')
}
