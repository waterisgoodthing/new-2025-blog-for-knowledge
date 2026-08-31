import { apiFetch } from './client'

export type QuestionType =
  | 'single_choice'
  | 'multiple_choice'
  | 'true_false'
  | 'short_answer'
  | 'essay'

export type Difficulty = 'unspecified' | 'easy' | 'medium' | 'hard'
export type QuestionStatus = 'active' | 'archived'
export type QuestionSourceType = 'manual' | 'book' | 'exam' | 'note' | 'url' | 'other'

export interface QuestionOption {
  key: string
  text: string
}

export interface AnswerData {
  kind: QuestionType
  value: string | string[] | boolean
  accepted?: string[]
  rubric?: string[]
}

export interface QuestionSource {
  id: string
  source_type: QuestionSourceType
  source_name: string | null
  source_title: string | null
  source_ref: string | null
  source_url: string | null
  source_note: string | null
  created_at: string
}

export interface Question {
  id: string
  subject_id: number
  title: string | null
  stem_md: string
  question_text: string
  question_type: QuestionType
  options: QuestionOption[]
  answer_data: AnswerData
  correct_answer: string | null
  analysis_md: string | null
  explanation: string | null
  difficulty: Difficulty
  status: QuestionStatus
  visibility: 'private'
  version: number
  knowledge_point_ids: number[]
  sources: QuestionSource[]
  created_at: string
  updated_at: string
}

export interface QuestionSourceInput {
  source_type?: QuestionSourceType
  source_title?: string | null
  source_ref?: string | null
  source_url?: string | null
  source_note?: string | null
}

export interface QuestionLinkInput {
  knowledge_point_id: number
  role?: 'primary' | 'secondary' | 'prerequisite'
  sort_order?: number
}

export interface QuestionCreateInput {
  subject_id: number
  title?: string | null
  stem_md: string
  question_type: QuestionType
  options?: QuestionOption[]
  answer_data: AnswerData
  analysis_md?: string | null
  difficulty?: Difficulty
  knowledge_point_links?: QuestionLinkInput[]
  sources?: QuestionSourceInput[]
}

export interface QuestionPatchInput extends Partial<Omit<QuestionCreateInput, 'subject_id'>> {
  version: number
  subject_id?: number
}

function queryString(filters: {
  subject_id?: number
  knowledge_point_id?: number
  status?: QuestionStatus
  type?: QuestionType
  difficulty?: Difficulty
}): string {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined) params.set(key, String(value))
  })
  const value = params.toString()
  return value ? `?${value}` : ''
}

export function listQuestions(
  filters: {
    subject_id?: number
    knowledge_point_id?: number
    status?: QuestionStatus
    type?: QuestionType
    difficulty?: Difficulty
  } = {},
): Promise<Question[]> {
  return apiFetch<Question[]>(`/api/admin/questions${queryString(filters)}`)
}

export function getQuestion(id: string): Promise<Question> {
  return apiFetch<Question>(`/api/admin/questions/${id}`)
}

export function createQuestion(input: QuestionCreateInput): Promise<Question> {
  return apiFetch<Question>('/api/admin/questions', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateQuestion(id: string, input: QuestionPatchInput): Promise<Question> {
  return apiFetch<Question>(`/api/admin/questions/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  })
}

export function updateLegacyQuestion(id: string, input: {
  version: number
  subject_id?: number
  title?: string | null
  question_text?: string
  question_type?: QuestionType
  options?: string[]
  correct_answer?: string | null
  explanation?: string | null
  difficulty?: Exclude<Difficulty, 'unspecified'> | null
  knowledge_point_ids?: number[]
}): Promise<Question> {
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
