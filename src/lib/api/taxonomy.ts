import { apiFetch } from './client'

export type TaxonomyStatus = 'active' | 'archived'

export interface Subject {
  id: number
  name: string
  description: string | null
  status: TaxonomyStatus
  sort_order: number
  created_at: string
  updated_at: string
}

export interface KnowledgePoint {
  id: number
  subject_id: number
  parent_id: number | null
  name: string
  description: string | null
  status: TaxonomyStatus
  sort_order: number
  created_at: string
  updated_at: string
}

export interface KnowledgePointTreeNode extends KnowledgePoint {
  children: KnowledgePointTreeNode[]
}

export interface KnowledgeTree {
  subject: Pick<Subject, 'id' | 'name'>
  nodes: KnowledgePointTreeNode[]
}

export interface SubjectInput {
  name: string
  description?: string | null
  status?: TaxonomyStatus
  sort_order?: number
}

export interface KnowledgePointInput {
  subject_id: number
  parent_id?: number | null
  name: string
  description?: string | null
  status?: TaxonomyStatus
  sort_order?: number
}

export type SubjectUpdate = Partial<SubjectInput>
export type KnowledgePointUpdate = Partial<KnowledgePointInput>

function queryString(filters: Record<string, string | number | boolean | undefined>): string {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined) params.set(key, String(value))
  })
  const query = params.toString()
  return query ? `?${query}` : ''
}

function normalizeStatusFilter(filters: {
  status?: TaxonomyStatus
  is_active?: boolean
}): { status?: TaxonomyStatus } {
  if (filters.status) return { status: filters.status }
  if (filters.is_active === true) return { status: 'active' }
  if (filters.is_active === false) return { status: 'archived' }
  return {}
}

export function listSubjects(
  filters: { status?: TaxonomyStatus; is_active?: boolean } = {},
): Promise<Subject[]> {
  return apiFetch<Subject[]>(
    `/api/admin/subjects${queryString(normalizeStatusFilter(filters))}`,
  )
}

export function getSubject(id: number): Promise<Subject> {
  return apiFetch<Subject>(`/api/admin/subjects/${id}`)
}

export function createSubject(input: SubjectInput): Promise<Subject> {
  return apiFetch<Subject>('/api/admin/subjects', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateSubject(id: number, input: SubjectUpdate): Promise<Subject> {
  return apiFetch<Subject>(`/api/admin/subjects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export function deleteSubject(id: number): Promise<void> {
  return apiFetch<void>(`/api/admin/subjects/${id}`, { method: 'DELETE' })
}

export function getSubjectKnowledgeTree(
  subjectId: number,
  filters: { status?: TaxonomyStatus } = {},
): Promise<KnowledgeTree> {
  return apiFetch<KnowledgeTree>(
    `/api/admin/subjects/${subjectId}/knowledge-tree${queryString(filters)}`,
  )
}

export function listKnowledgePoints(
  filters: {
    subject_id?: number
    parent_id?: number
    status?: TaxonomyStatus
    is_active?: boolean
  } = {},
): Promise<KnowledgePoint[]> {
  const { is_active: _isActive, status, ...rest } = filters
  return apiFetch<KnowledgePoint[]>(
    `/api/admin/knowledge-points${queryString({
      ...rest,
      ...normalizeStatusFilter({ status, is_active: _isActive }),
    })}`,
  )
}

export function getKnowledgePoint(id: number): Promise<KnowledgePoint> {
  return apiFetch<KnowledgePoint>(`/api/admin/knowledge-points/${id}`)
}

export function createKnowledgePoint(input: KnowledgePointInput): Promise<KnowledgePoint> {
  return apiFetch<KnowledgePoint>('/api/admin/knowledge-points', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateKnowledgePoint(
  id: number,
  input: KnowledgePointUpdate,
): Promise<KnowledgePoint> {
  return apiFetch<KnowledgePoint>(`/api/admin/knowledge-points/${id}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export function archiveKnowledgePoint(id: number): Promise<KnowledgePoint> {
  return apiFetch<KnowledgePoint>(`/api/admin/knowledge-points/${id}/archive`, {
    method: 'POST',
  })
}

export function deleteKnowledgePoint(id: number): Promise<void> {
  return apiFetch<void>(`/api/admin/knowledge-points/${id}`, { method: 'DELETE' })
}
