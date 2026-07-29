import { describe, expect, it, vi } from 'vitest'
import { searchWorkspace } from './search'

describe('searchWorkspace', () => {
  it('uses the admin search contract without inventing results', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify([]), { status: 200 }))
    await expect(searchWorkspace('network')).resolves.toEqual([])
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/api/admin/search'), expect.objectContaining({ method: 'POST' }))
    fetchMock.mockRestore()
  })
})
