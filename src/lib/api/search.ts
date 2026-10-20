import { apiFetch } from './client'

export interface SearchResult {
  id: string
  slug: string
  title: string
  type: string
  status: string
  hidden: boolean
  updated_at: string
}

export async function searchWorkspace(query: string, limit = 50): Promise<SearchResult[]> {
  return apiFetch<SearchResult[]>('/api/admin/search', {
    method: 'POST',
    body: JSON.stringify({ query, limit }),
  })
}
