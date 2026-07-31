import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getMe, login } = vi.hoisted(() => ({ getMe: vi.fn(), login: vi.fn() }))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}))

vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <a href={String(href)} {...props}>{children}</a>
  ),
}))

vi.mock('next/image', () => ({
  default: (props: React.ImgHTMLAttributes<HTMLImageElement>) => <img {...props} />,
}))

vi.mock('@/hooks/use-note-index', () => ({
  useNoteIndex: () => ({ data: undefined, isLoading: false, mutate: vi.fn() }),
}))

vi.mock('@/lib/api/auth', () => ({
  getMe,
  login,
  logout: vi.fn(),
  loginWithPasskey: vi.fn(),
  isPasskeyAvailable: () => false,
  checkPasskeyRegistered: vi.fn(),
}))

vi.mock('@/app/(home)/stores/config-store', () => ({
  useConfigStore: () => ({
    siteContent: {
      avatarUrl: '/images/avatar.png',
      meta: { title: 'My Blog' },
    },
  }),
}))

vi.mock('./music-tab', () => ({ MusicTab: () => null }))
vi.mock('./recommendation-tab', () => ({ RecommendationTab: () => null }))
vi.mock('./ai-tab', () => ({ AITab: () => null }))
vi.mock('./security-tab', () => ({ SecurityTab: () => null }))
vi.mock('./audit-tab', () => ({ AuditTab: () => null }))
vi.mock('@/app/notes/components/knowledge-sidebar', () => ({ KnowledgeSidebar: () => null }))
vi.mock('@/app/notes/components/suggestion-card', () => ({ SuggestionCard: () => null }))
vi.mock('@/app/(home)/config-dialog/site-settings-panel', () => ({ SiteSettingsPanel: () => null }))

import ManagePage from './page'

describe('/manage admin boundary', () => {
  beforeEach(() => {
    getMe.mockReset()
    login.mockReset()
  })

  it('shows the login state when the current session belongs to a non-admin user', async () => {
    getMe.mockResolvedValue({
      id: 'reader-1',
      username: 'reader',
      is_admin: false,
      auth_level: 'password',
    })

    render(<ManagePage />)

    await waitFor(() => expect(screen.getByRole('heading', { name: 'My Blog' })).toBeInTheDocument())
    expect(screen.queryByRole('heading', { name: '管理面板' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: '删除' })).not.toBeInTheDocument()
  })

  it('keeps a non-admin user on the login state after password authentication', async () => {
    getMe
      .mockRejectedValueOnce(new Error('Not authenticated'))
      .mockResolvedValueOnce({
        id: 'reader-2',
        username: 'reader',
        is_admin: false,
        auth_level: 'password',
      })
    login.mockResolvedValue({ message: 'Login successful' })

    render(<ManagePage />)
    await waitFor(() => expect(screen.getByRole('heading', { name: 'My Blog' })).toBeInTheDocument())

    fireEvent.change(screen.getByRole('textbox', { name: '用户名' }), { target: { value: 'reader' } })
    fireEvent.change(screen.getByLabelText('密码'), { target: { value: 'password' } })
    fireEvent.click(screen.getByRole('button', { name: '密码登录' }))

    await waitFor(() => expect(getMe).toHaveBeenCalledTimes(2))
    expect(screen.getByRole('heading', { name: 'My Blog' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: '管理面板' })).not.toBeInTheDocument()
  })

  it('shows the management panel only for a current admin user', async () => {
    getMe.mockResolvedValue({
      id: 'admin-1',
      username: 'owner',
      is_admin: true,
      auth_level: 'password',
    })

    render(<ManagePage />)

    await waitFor(() => expect(screen.getByRole('heading', { name: '管理面板' })).toBeInTheDocument())
    expect(screen.getByText('owner')).toBeInTheDocument()
  })
})
