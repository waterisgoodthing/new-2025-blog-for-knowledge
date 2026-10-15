import { render, screen, waitFor } from '@testing-library/react'
import { SWRConfig } from 'swr'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getMe, replace } = vi.hoisted(() => ({
  getMe: vi.fn(),
  replace: vi.fn(),
}))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace }),
}))

vi.mock('@/lib/api/auth', () => ({
  getMe,
}))

import { AuthGate } from './auth-gate'

describe('AuthGate', () => {
  beforeEach(() => {
    getMe.mockReset()
    replace.mockReset()
  })

  it('revalidates a new protected entry instead of trusting a cached admin result', async () => {
    const cache = new Map()
    getMe
      .mockResolvedValueOnce({ id: 'admin-1', username: 'owner', is_admin: true, auth_level: 'password' })
      .mockResolvedValueOnce({ id: 'admin-1', username: 'owner', is_admin: false, auth_level: 'password' })

    const first = render(
      <SWRConfig value={{ provider: () => cache }}>
        <AuthGate><div>private management content</div></AuthGate>
      </SWRConfig>,
    )

    await waitFor(() => expect(screen.getByText('private management content')).toBeInTheDocument())
    first.unmount()

    render(
      <SWRConfig value={{ provider: () => cache }}>
        <AuthGate><div>private management content</div></AuthGate>
      </SWRConfig>,
    )

    await waitFor(() => expect(getMe).toHaveBeenCalledTimes(2))
    await waitFor(() => expect(replace).toHaveBeenCalledWith('/manage'))
    expect(screen.queryByText('private management content')).not.toBeInTheDocument()
  })

  it('rechecks a mounted protected page when focus returns after an admin downgrade', async () => {
    getMe
      .mockResolvedValueOnce({ id: 'admin-2', username: 'owner', is_admin: true, auth_level: 'password' })
      .mockResolvedValueOnce({ id: 'admin-2', username: 'owner', is_admin: false, auth_level: 'password' })

    render(
      <SWRConfig value={{ provider: () => new Map(), focusThrottleInterval: 32 }}>
        <AuthGate><div>private management content</div></AuthGate>
      </SWRConfig>,
    )

    await waitFor(() => expect(screen.getByText('private management content')).toBeInTheDocument())
    await new Promise(resolve => setTimeout(resolve, 40))
    window.dispatchEvent(new Event('focus'))

    await waitFor(() => expect(getMe).toHaveBeenCalledTimes(2))
    await waitFor(() => expect(replace).toHaveBeenCalledWith('/manage'))
    expect(screen.queryByText('private management content')).not.toBeInTheDocument()
  })
})
