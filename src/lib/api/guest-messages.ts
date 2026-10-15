import { apiFetch } from './client'

export interface GuestMessage {
  id: string
  content: string
  nickname: string | null
  attachment_type: string | null
  attachment_slug: string | null
  status: string
  created_at: string
}

export interface GuestMessageListResponse {
  items: GuestMessage[]
  total: number
  page: number
  size: number
}

export interface GuestMessageCreateInput {
  content: string
  nickname?: string
  attachment_type?: 'home' | 'blog' | 'note' | 'mistake'
  attachment_slug?: string
}

export async function createGuestMessage(data: GuestMessageCreateInput): Promise<GuestMessage> {
  return apiFetch<GuestMessage>('/api/guest-messages', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function listGuestMessages(params: {
  attachment_type?: string
  attachment_slug?: string
  status?: 'visible' | 'hidden' | 'deleted'
  page?: number
  size?: number
} = {}): Promise<GuestMessageListResponse> {
  const searchParams = new URLSearchParams()
  if (params.attachment_type) searchParams.set('attachment_type', params.attachment_type)
  if (params.attachment_slug) searchParams.set('attachment_slug', params.attachment_slug)
  if (params.status) searchParams.set('status', params.status)
  if (params.page) searchParams.set('page', String(params.page))
  if (params.size) searchParams.set('size', String(params.size))
  const qs = searchParams.toString()
  return apiFetch<GuestMessageListResponse>(`/api/guest-messages${qs ? `?${qs}` : ''}`)
}

export async function moderateGuestMessage(
  messageId: string,
  status: 'visible' | 'hidden' | 'deleted'
): Promise<GuestMessage> {
  return apiFetch<GuestMessage>(`/api/guest-messages/${messageId}/moderate`, {
    method: 'PUT',
    body: JSON.stringify({ status }),
  })
}
