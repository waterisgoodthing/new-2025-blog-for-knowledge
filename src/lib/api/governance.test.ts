import { describe, expect, it, vi } from 'vitest'

vi.mock('./client', () => ({ apiFetch: vi.fn() }))

const { apiFetch } = await import('./client')
const { getGovernanceSummary } = await import('./governance')

describe('governance API', () => {
  it('uses the admin governance summary endpoint', async () => {
    vi.mocked(apiFetch).mockResolvedValue({})
    await getGovernanceSummary()
    expect(apiFetch).toHaveBeenCalledWith('/api/admin/governance/summary')
  })
})
