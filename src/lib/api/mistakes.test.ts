import { describe, expect, it, vi } from 'vitest'
import {
  listPublicMistakes,
  updateMistakeVisibility,
  type PublicMistake,
} from './mistakes'

const PUBLIC_MISTAKE_DTO_ALLOWLIST = [
  'id',
  'title',
  'question_text',
  'correct_answer',
  'analysis',
  'reason_category',
  'mistake_reason',
  'difficulty',
  'knowledge_point_ids',
  'created_at',
  'updated_at',
] as const

const publicMistakeFixture: PublicMistake = {
  id: '11111111-1111-1111-1111-111111111111',
  title: '公开错题标题',
  question_text: '题干',
  correct_answer: 'B',
  analysis: '解析',
  reason_category: 'concept',
  mistake_reason: '概念混淆',
  difficulty: 'medium',
  knowledge_point_ids: [1, 2],
  created_at: '2026-09-01T00:00:00Z',
  updated_at: '2026-09-02T00:00:00Z',
}

describe('PublicMistake DTO allowlist (W3-D03)', () => {
  it('has exactly the 11 contract fields and nothing else', () => {
    expect(Object.keys(publicMistakeFixture).sort()).toEqual(
      [...PUBLIC_MISTAKE_DTO_ALLOWLIST].sort(),
    )
  })

  it('does not carry private fields such as my_answer', () => {
    const keys = Object.keys(publicMistakeFixture)
    expect(keys).not.toContain('my_answer')
    expect(keys).not.toContain('visibility')
    expect(keys).not.toContain('status')
    expect(keys).not.toContain('version')
  })
})

describe('listPublicMistakes', () => {
  it('reads the anonymous public endpoint without a query when no params are given', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({ items: [], total: 0, page: 1, size: 20, empty: true, message: '当前没有公开错题' }),
        { status: 200 },
      ),
    )

    await expect(listPublicMistakes()).resolves.toEqual({
      items: [],
      total: 0,
      page: 1,
      size: 20,
      empty: true,
      message: '当前没有公开错题',
    })
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/public/mistakes'),
      expect.objectContaining({ credentials: 'include' }),
    )
    expect(fetchMock.mock.calls[0][0]).not.toContain('?')
    fetchMock.mockRestore()
  })

  it('forwards page and size as query params', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({ items: [publicMistakeFixture], total: 1, page: 2, size: 10, empty: false, message: null }),
        { status: 200 },
      ),
    )

    const response = await listPublicMistakes({ page: 2, size: 10 })
    expect(response.items).toHaveLength(1)
    expect(response.empty).toBe(false)
    expect(fetchMock.mock.calls[0][0]).toContain('/api/public/mistakes?page=2&size=10')
    fetchMock.mockRestore()
  })
})

describe('updateMistakeVisibility', () => {
  it('PATCHes admin visibility with the optimistic version lock', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ id: '11111111-1111-1111-1111-111111111111' }), { status: 200 }),
    )

    await updateMistakeVisibility('11111111-1111-1111-1111-111111111111', {
      visibility: 'public',
      version: 3,
    })

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/admin/mistakes/11111111-1111-1111-1111-111111111111/visibility'),
      expect.objectContaining({
        method: 'PATCH',
        credentials: 'include',
        body: JSON.stringify({ visibility: 'public', version: 3 }),
      }),
    )
    fetchMock.mockRestore()
  })
})
