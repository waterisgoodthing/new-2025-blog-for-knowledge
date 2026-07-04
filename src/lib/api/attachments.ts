import { apiFetch } from './client'
import { getApiBase } from './config'

export type AttachmentVisibility = 'private'
export type AttachmentStatus = 'active' | 'missing' | 'deleted'
export type AttachmentTargetType = 'question_draft' | 'question' | 'mistake'
export type AttachmentPurpose =
  | 'source'
  | 'question'
  | 'answer'
  | 'inline'
  | 'ai_input'
  | 'ai_output'

export interface Attachment {
  id: string
  original_name: string
  storage_provider: 'local'
  mime_type: string
  size_bytes: number
  checksum_sha256: string
  visibility: AttachmentVisibility
  status: AttachmentStatus
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface AttachmentLink {
  id: string
  attachment_id: string
  target_type: AttachmentTargetType
  target_id: string
  purpose: AttachmentPurpose
  sort_order: number
  created_at: string
}

export interface AttachmentLinkCreate {
  attachment_id: string
  target_type: AttachmentTargetType
  target_id: string
  purpose: AttachmentPurpose
  sort_order?: number
}

function queryString(filters: Record<string, string | number | undefined>): string {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined) params.set(key, String(value))
  })
  const query = params.toString()
  return query ? `?${query}` : ''
}

export function listAttachments(filters: { status?: AttachmentStatus } = {}): Promise<Attachment[]> {
  return apiFetch<Attachment[]>(`/api/admin/attachments${queryString(filters)}`)
}

export function uploadAttachment(file: File): Promise<Attachment> {
  const body = new FormData()
  body.set('file', file)
  return apiFetch<Attachment>('/api/admin/attachments', {
    method: 'POST',
    body,
  })
}

export function getAttachment(id: string): Promise<Attachment> {
  return apiFetch<Attachment>(`/api/admin/attachments/${id}`)
}

export function getAttachmentContentUrl(id: string): string {
  return `${getApiBase()}/api/admin/attachments/${id}/content`
}

export function deleteAttachment(id: string): Promise<Attachment> {
  return apiFetch<Attachment>(`/api/admin/attachments/${id}`, {
    method: 'DELETE',
  })
}

export function listAttachmentLinks(
  filters: {
    target_type?: AttachmentTargetType
    target_id?: string
    attachment_id?: string
  } = {},
): Promise<AttachmentLink[]> {
  return apiFetch<AttachmentLink[]>(
    `/api/admin/attachment-links${queryString(filters)}`,
  )
}

export function createAttachmentLink(input: AttachmentLinkCreate): Promise<AttachmentLink> {
  return apiFetch<AttachmentLink>('/api/admin/attachment-links', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function deleteAttachmentLink(id: string): Promise<void> {
  return apiFetch<void>(`/api/admin/attachment-links/${id}`, {
    method: 'DELETE',
  })
}
