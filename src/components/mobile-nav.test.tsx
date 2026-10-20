import { render, screen } from '@testing-library/react'
import type { ComponentProps, ReactNode } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

let pathname = '/'
let authState = { isAdmin: false, isLoading: true }

vi.mock('next/navigation', () => ({
  usePathname: () => pathname,
}))

vi.mock('next/link', () => ({
  default: ({ href, children, ...props }: { href: string; children: ReactNode }) => (
    <a href={href} {...props}>{children}</a>
  ),
}))

vi.mock('@/hooks/use-admin-auth', () => ({
  useAdminAuth: () => authState,
}))

vi.mock('motion/react', () => ({
  AnimatePresence: ({ children }: { children: ReactNode }) => children,
  motion: {
    div: ({ children, ...props }: ComponentProps<'div'>) => <div {...props}>{children}</div>,
  },
}))

vi.mock('@/svgs/scroll-outline.svg', () => ({ default: () => <span /> }))
vi.mock('@/svgs/scroll-filled.svg', () => ({ default: () => <span /> }))
vi.mock('@/svgs/projects-filled.svg', () => ({ default: () => <span /> }))
vi.mock('@/svgs/projects-outline.svg', () => ({ default: () => <span /> }))
vi.mock('@/svgs/about-filled.svg', () => ({ default: () => <span /> }))
vi.mock('@/svgs/about-outline.svg', () => ({ default: () => <span /> }))

const { default: MobileNav } = await import('./mobile-nav')

describe('MobileNav', () => {
  beforeEach(() => {
    pathname = '/'
    authState = { isAdmin: false, isLoading: true }
  })

  it('renders public destinations immediately without exposing management while auth is unresolved', () => {
    render(<MobileNav />)

    expect(screen.getByRole('link', { name: '首页' })).toHaveAttribute('href', '/')
    expect(screen.getByRole('link', { name: '博客' })).toHaveAttribute('href', '/blog')
    expect(screen.getByRole('link', { name: '笔记' })).toHaveAttribute('href', '/notes')
    expect(screen.getByRole('link', { name: '错题' })).toHaveAttribute('href', '/mistakes')
    expect(screen.queryByRole('link', { name: '管理' })).not.toBeInTheDocument()
  })

  it('adds the management destination only after an administrator session is confirmed', () => {
    authState = { isAdmin: true, isLoading: false }

    render(<MobileNav />)

    expect(screen.getByRole('link', { name: '管理' })).toHaveAttribute('href', '/manage/dashboard')
  })
})
