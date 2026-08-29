import { render, screen, waitFor } from '@testing-library/react'
import { SWRConfig } from 'swr'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getMe, getSessionState } = vi.hoisted(() => ({
	getMe: vi.fn(),
	getSessionState: vi.fn()
}))

vi.mock('@/lib/api/auth', () => ({ getMe, getSessionState }))

import { useAdminAuth } from './use-admin-auth'

function Probe({ mode }: { mode?: 'optional' | 'strict' }) {
	const { error, isAdmin, isLoading } = useAdminAuth({ mode })
	return <output>{JSON.stringify({ error: error?.message ?? null, isAdmin, isLoading })}</output>
}

function renderProbe(mode: 'optional' | 'strict') {
	return render(
		<SWRConfig value={{ provider: () => new Map() }}>
			<Probe mode={mode} />
		</SWRConfig>
	)
}

describe('useAdminAuth modes', () => {
	beforeEach(() => {
		getMe.mockReset()
		getSessionState.mockReset()
	})

	it('uses the optional endpoint without requesting strict identity', async () => {
		getSessionState.mockResolvedValue({ authenticated: false, is_admin: false })

		renderProbe('optional')

		await waitFor(() => expect(screen.getByText(/"isLoading":false/)).toBeInTheDocument())
		expect(getSessionState).toHaveBeenCalledTimes(1)
		expect(getMe).not.toHaveBeenCalled()
		expect(screen.getByText(/"isAdmin":false/)).toBeInTheDocument()
	})

	it('keeps strict mode on the existing identity endpoint', async () => {
		getMe.mockResolvedValue({ id: 'admin-1', username: 'owner', is_admin: true, auth_level: 'password' })

		renderProbe('strict')

		await waitFor(() => expect(screen.getByText(/"isAdmin":true/)).toBeInTheDocument())
		expect(getMe).toHaveBeenCalledTimes(1)
		expect(getSessionState).not.toHaveBeenCalled()
	})

	it('fails optional state safely while preserving the diagnostic error', async () => {
		getSessionState.mockRejectedValue(new Error('isolated optional-session outage'))

		renderProbe('optional')

		await waitFor(() => expect(screen.getByText(/isolated optional-session outage/)).toBeInTheDocument())
		expect(screen.getByText(/"isAdmin":false/)).toBeInTheDocument()
		expect(getMe).not.toHaveBeenCalled()
	})
})
