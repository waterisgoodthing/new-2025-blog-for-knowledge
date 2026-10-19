import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

/**
 * Public navigation cutover (Phase 5).
 *
 * The layout is the single place where the public desktop/mobile navigation is
 * chosen, so these tests pin the mount rules:
 * - inner pages (desktop) get the glass top navigation,
 * - the home page keeps NavCard only (no top bar, no overlap),
 * - mobile gets the hamburger drawer instead of the bottom tab bar,
 * - the administrator entry is only added when the optional session says so.
 */

const state = {
	pathname: '/blog',
	maxSM: false,
	isAdmin: false
}

vi.mock('next/navigation', () => ({
	usePathname: () => state.pathname,
	useRouter: () => ({ push: vi.fn() })
}))

vi.mock('@/hooks/use-size', () => ({
	useSize: () => ({ maxSM: state.maxSM, init: true }),
	useSizeInit: () => undefined
}))

vi.mock('@/hooks/use-center', () => ({ useCenterInit: () => undefined }))

vi.mock('@/hooks/use-admin-auth', () => ({
	useAdminAuth: () => ({ isAdmin: state.isAdmin, isLoading: false })
}))

vi.mock('@/app/(home)/stores/config-store', () => ({
	useConfigStore: () => ({
		cardStyles: { musicCard: { enabled: false } },
		siteContent: { meta: { title: 'My Blog' }, backgroundColors: [] },
		regenerateKey: 0
	})
}))

vi.mock('./backgrounds/blurred-bubbles', () => ({ default: () => null }))
vi.mock('sonner', () => ({ Toaster: () => null }))
vi.mock('@/components/nav-card', () => ({ default: () => <div data-testid='nav-card' /> }))
vi.mock('@/components/vertical-nav', () => ({ default: () => <div data-testid='vertical-nav' /> }))
vi.mock('@/components/mobile-nav', () => ({ default: () => <div data-testid='mobile-nav' /> }))
vi.mock('@/components/music-card', () => ({ default: () => null }))
vi.mock('@/components/scroll-top-button', () => ({ ScrollTopButton: () => null }))
vi.mock('@/components/site-settings-loader', () => ({ SiteSettingsLoader: () => null }))

import Layout from './index'

beforeEach(() => {
	state.pathname = '/blog'
	state.maxSM = false
	state.isAdmin = false
})

const renderLayout = () =>
	render(
		<Layout>
			<p>page body</p>
		</Layout>
	)

describe('public layout — desktop navigation', () => {
	it('mounts the glass top navigation on inner pages', () => {
		renderLayout()

		expect(screen.getByRole('navigation', { name: '主导航' })).toBeInTheDocument()
		expect(screen.queryByTestId('vertical-nav')).not.toBeInTheDocument()
		expect(screen.getByText('page body')).toBeInTheDocument()
	})

	it('keeps NavCard and skips the top bar on the home page', () => {
		state.pathname = '/'
		renderLayout()

		expect(screen.queryByRole('navigation', { name: '主导航' })).not.toBeInTheDocument()
		expect(screen.getByTestId('nav-card')).toBeInTheDocument()
	})

	it('renders no public navigation on /write', () => {
		state.pathname = '/write/hello'
		renderLayout()

		expect(screen.queryByRole('navigation', { name: '主导航' })).not.toBeInTheDocument()
		expect(screen.queryByRole('button', { name: '打开导航菜单' })).not.toBeInTheDocument()
		expect(screen.queryByTestId('vertical-nav')).not.toBeInTheDocument()
		expect(screen.queryByTestId('mobile-nav')).not.toBeInTheDocument()
	})

	it('never stacks the public bar on the administrator shell routes', () => {
		for (const pathname of ['/manage', '/manage/dashboard', '/manage/notes']) {
			state.pathname = pathname
			const { unmount } = renderLayout()

			expect(screen.queryByRole('navigation', { name: '主导航' })).not.toBeInTheDocument()
			expect(screen.queryByRole('button', { name: '打开导航菜单' })).not.toBeInTheDocument()
			unmount()
		}
	})
})

describe('public layout — administrator entry', () => {
	it('omits the administrator entry for anonymous visitors', () => {
		renderLayout()

		expect(screen.queryByRole('link', { name: '管理后台' })).not.toBeInTheDocument()
	})

	it('adds the administrator entry when the optional session resolves to admin', () => {
		state.isAdmin = true
		renderLayout()

		const adminLink = screen.getByRole('link', { name: '管理后台' })
		expect(adminLink).toHaveAttribute('href', '/manage')
	})
})

describe('public layout — mobile navigation', () => {
	it('replaces the bottom tab bar with the drawer trigger', () => {
		state.maxSM = true
		state.pathname = '/notes'
		renderLayout()

		expect(screen.getByRole('button', { name: '打开导航菜单' })).toBeInTheDocument()
		expect(screen.queryByTestId('mobile-nav')).not.toBeInTheDocument()
		// The desktop bar must not double up on mobile.
		expect(screen.queryByRole('navigation', { name: '主导航' })).not.toBeInTheDocument()
	})

	it('adds the administrator destination to the mobile drawer for admins', async () => {
		state.maxSM = true
		state.isAdmin = true
		state.pathname = '/notes'
		renderLayout()

		const trigger = screen.getByRole('button', { name: '打开导航菜单' })
		expect(trigger).toBeInTheDocument()
		trigger.focus()
		fireEvent.click(trigger)

		// The drawer only mounts its groups once open.
		expect(await screen.findByRole('link', { name: '管理后台' })).toHaveAttribute('href', '/manage')
	})
})
