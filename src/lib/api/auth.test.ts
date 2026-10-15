import { beforeEach, describe, expect, it, vi } from 'vitest'

const { apiFetch } = vi.hoisted(() => ({ apiFetch: vi.fn() }))

vi.mock('./client', () => ({ apiFetch }))

import { getSessionState } from './auth'

describe('optional session-state API client', () => {
	beforeEach(() => {
		apiFetch.mockReset()
	})

	it('requests only the minimal optional session-state endpoint', async () => {
		apiFetch.mockResolvedValue({ authenticated: false, is_admin: false })

		await expect(getSessionState()).resolves.toEqual({ authenticated: false, is_admin: false })
		expect(apiFetch).toHaveBeenCalledWith('/api/auth/session-state')
	})
})
