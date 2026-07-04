import { apiFetch } from './client'

export interface Subject {
  id: number
  name: string
  description: string | null
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface Chapter {
  id: number
  subject_id: number
  name: string
  description: string | null
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface KnowledgePoint {
  id: number
  subject_id: number
  chapter_id: number | null
  name: string
  description: string | null
  is_active: boolean
  sort_order: number
  created_at: string
  updated_at: string
}

export interface SubjectInput {
  name: string
  description?: string | null
  is_active?: boolean
  sort_order?: number
}

export interface ChapterInput {
  subject_id: number
  name: string
  description?: string | null
  is_active?: boolean
  sort_order?: number
}

export interface KnowledgePointInput {
  subject_id: number
  chapter_id?: number | null
  name: string
  description?: string | null
  is_active?: boolean
  sort_order?: number
}

export type SubjectUpdate = Partial<SubjectInput>
export type ChapterUpdate = Partial<Omit<ChapterInput, 'subject_id'>>
export type KnowledgePointUpdate = Partial<KnowledgePointInput>

function queryString(filters: Record<string, string | number | boolean | undefined>): string {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined) params.set(key, String(value))
  })
  const query = params.toString()
  return query ? `?${query}` : ''
}

export function listSubjects(filters: { is_active?: boolean } = {}): Promise<Subject[]> {
  return apiFetch<Subject[]>(`/api/subjects${queryString(filters)}`)
}

export function getSubject(id: number): Promise<Subject> {
  return apiFetch<Subject>(`/api/subjects/${id}`)
}

export function createSubject(input: SubjectInput): Promise<Subject> {
  return apiFetch<Subject>('/api/subjects', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateSubject(id: number, input: SubjectUpdate): Promise<Subject> {
  return apiFetch<Subject>(`/api/subjects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export function deleteSubject(id: number): Promise<void> {
  return apiFetch<void>(`/api/subjects/${id}`, { method: 'DELETE' })
}

export function listChapters(
  filters: { subject_id?: number; is_active?: boolean } = {},
): Promise<Chapter[]> {
  return apiFetch<Chapter[]>(`/api/chapters${queryString(filters)}`)
}

export function getChapter(id: number): Promise<Chapter> {
  return apiFetch<Chapter>(`/api/chapters/${id}`)
}

export function createChapter(input: ChapterInput): Promise<Chapter> {
  return apiFetch<Chapter>('/api/chapters', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateChapter(id: number, input: ChapterUpdate): Promise<Chapter> {
  return apiFetch<Chapter>(`/api/chapters/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export function deleteChapter(id: number): Promise<void> {
  return apiFetch<void>(`/api/chapters/${id}`, { method: 'DELETE' })
}

export function listKnowledgePoints(
  filters: { subject_id?: number; chapter_id?: number; is_active?: boolean } = {},
): Promise<KnowledgePoint[]> {
  return apiFetch<KnowledgePoint[]>(`/api/knowledge-points${queryString(filters)}`)
}

export function getKnowledgePoint(id: number): Promise<KnowledgePoint> {
  return apiFetch<KnowledgePoint>(`/api/knowledge-points/${id}`)
}

export function createKnowledgePoint(input: KnowledgePointInput): Promise<KnowledgePoint> {
  return apiFetch<KnowledgePoint>('/api/knowledge-points', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateKnowledgePoint(
  id: number,
  input: KnowledgePointUpdate,
): Promise<KnowledgePoint> {
  return apiFetch<KnowledgePoint>(`/api/knowledge-points/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export function deleteKnowledgePoint(id: number): Promise<void> {
  return apiFetch<void>(`/api/knowledge-points/${id}`, { method: 'DELETE' })
}
