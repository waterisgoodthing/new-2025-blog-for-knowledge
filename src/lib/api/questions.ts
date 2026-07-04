import { apiFetch } from './client'

export type QuestionType =
  | 'single_choice'
  | 'multiple_choice'
  | 'true_false'
  | 'short_answer'
  | 'essay'

export type Difficulty = 'easy' | 'medium' | 'hard'
export type QuestionStatus = 'active' | 'archived'

export interface QuestionSource {
  id: string
  source_type: 'manual'
  source_name: string | null
  source_ref: string
  created_at: string
}

export interface Question {
  id: string
  subject_id: number
  title: string | null
  question_text: string
  question_type: QuestionType
  options: string[]
  correct_answer: string | null
  explanation: string | null
  difficulty: Difficulty | null
  status: QuestionStatus
  visibility: 'private'
  version: number
  knowledge_point_ids: number[]
  sources: QuestionSource[]
  created_at: string
  updated_at: string
}

export interface QuestionUpdate {
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

function queryString(filters: {
  subject_id?: number
  status?: QuestionStatus
}): string {
  const params = new URLSearchParams()
  if (filters.subject_id !== undefined) {
    params.set('subject_id', String(filters.subject_id))
  }
  if (filters.status !== undefined) params.set('status', filters.status)
  const value = params.toString()
  return value ? `?${value}` : ''
}

export function listQuestions(
  filters: { subject_id?: number; status?: QuestionStatus } = {},
): Promise<Question[]> {
  return apiFetch<Question[]>(`/api/admin/questions${queryString(filters)}`)
}

export function getQuestion(id: string): Promise<Question> {
  return apiFetch<Question>(`/api/admin/questions/${id}`)
}

export function updateQuestion(id: string, input: QuestionUpdate): Promise<Question> {
  return apiFetch<Question>(`/api/admin/questions/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export function archiveQuestion(id: string, version: number): Promise<Question> {
  return apiFetch<Question>(`/api/admin/questions/${id}`, {
    method: 'DELETE',
    body: JSON.stringify({ version }),
  })
}
