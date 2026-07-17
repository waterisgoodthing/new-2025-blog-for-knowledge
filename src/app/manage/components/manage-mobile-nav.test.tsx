import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'

vi.mock('next/navigation', () => ({
  usePathname: () => '/manage/dashboard',
}))

vi.mock('next/link', () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}))

vi.mock('lucide-react', () => ({
  Menu: () => <span data-testid='menu-icon' />,
  X: () => <span data-testid='x-icon' />,
}))

const mockNavItems = [
  {
    href: '/manage/dashboard',
    label: '今天',
    icon: () => <span />,
    match: (p: string) => p === '/manage/dashboard',
  },
  {
    href: '/manage/capture',
    label: '收进来',
    icon: () => <span />,
    match: (p: string) => p === '/manage/capture',
  },
]

vi.mock('./manage-sidebar', () => ({
  navGroups: [
    {
      title: '今日学习',
      items: mockNavItems,
    },
  ],
  allItems: mockNavItems,
}))

vi.mock('@/lib/utils', () => ({
  cn: (...classes: unknown[]) => classes.filter(Boolean).join(' '),
}))

const { ManageMobileNav } = await import('./manage-mobile-nav')

describe('ManageMobileNav — drawer background isolation (R-03)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('inerts main content when drawer is open', async () => {
    render(
      <section>
        <ManageMobileNav />
        <main data-testid='main-content'>page content</main>
      </section>,
    )

    // Initially, main is not inerted
    expect(screen.getByTestId('main-content').hasAttribute('inert')).toBe(false)

    // Open the drawer
    fireEvent.click(screen.getByRole('button', { name: '打开导航菜单' }))

    // Wait for the dialog to appear and main to be inerted
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
    await waitFor(() => {
      expect(screen.getByTestId('main-content').closest('[inert]')).not.toBeNull()
    })

    // The drawer itself must NOT be inerted
    expect(screen.getByRole('dialog').hasAttribute('inert')).toBe(false)
  })

  it('removes inert from main content when drawer is closed via Escape', async () => {
    render(
      <section>
        <ManageMobileNav />
        <main data-testid='main-content'>page content</main>
      </section>,
    )

    // Open the drawer
    fireEvent.click(screen.getByRole('button', { name: '打开导航菜单' }))

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
    await waitFor(() => {
      expect(screen.getByTestId('main-content').closest('[inert]')).not.toBeNull()
    })

    // Close via Escape
    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Escape' })

    // Wait for dialog to disappear and inert to be removed
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    })
    await waitFor(() => {
      expect(screen.getByTestId('main-content').closest('[inert]')).toBeNull()
    })
  })

  it('inerts topbar as well as main when drawer is open', async () => {
    const { container } = render(
      <section>
        <ManageMobileNav />
        <main data-testid='main-content'>page content</main>
      </section>,
    )

    // Open the drawer
    fireEvent.click(screen.getByRole('button', { name: '打开导航菜单' }))

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    const section = container.querySelector('section')
    expect(section?.closest('[inert]')).not.toBeNull()
  })

  it('inerts background branches outside the workspace section', async () => {
    render(
      <div>
        <section>
          <ManageMobileNav />
          <main data-testid='main-content'>page content</main>
        </section>
        <nav data-testid='site-mobile-nav'>site navigation</nav>
      </div>,
    )

    fireEvent.click(screen.getByRole('button', { name: '打开导航菜单' }))

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })

    expect(screen.getByTestId('site-mobile-nav').closest('[inert]')).not.toBeNull()
  })

  it('mounts the dialog at body level so it covers the full viewport', async () => {
    render(
      <section>
        <ManageMobileNav />
        <main>page content</main>
      </section>,
    )

    fireEvent.click(screen.getByRole('button', { name: '打开导航菜单' }))

    await waitFor(() => {
      expect(screen.getByRole('dialog').parentElement).toBe(document.body)
    })
  })
})
