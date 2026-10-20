'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

import { AuthGate } from '@/components/auth-gate'
import { AdminSidebar, MobileDrawer, Uiv2AppShell } from '@/components/ui-v2'
import { navGroups } from '../components/manage-sidebar'
import { ManageTopbar } from '../components/manage-topbar'

/**
 * Manage workspace shell (VSC-13).
 *
 * `AuthGate` stays the outermost element: navigation visibility is presentation
 * only and the backend `get_current_admin` dependency remains the real boundary.
 * The legacy `ManageSidebar` / `ManageMobileNav` files are kept (and still
 * tested) but are no longer rendered here.
 */
export default function ManageWorkspaceLayout({ children }: Readonly<{ children: React.ReactNode }>) {
	const pathname = usePathname()

	return (
		<AuthGate>
			<Uiv2AppShell
				variant='admin'
				currentPath={pathname}
				sidebar={<AdminSidebar groups={navGroups} currentPath={pathname} />}
				mobileNav={
					<MobileDrawer
						groups={navGroups}
						currentPath={pathname}
						action={
							<Link
								href='/'
								aria-label='返回公开首页'
								className='inline-flex h-8 items-center rounded-lg px-2 text-xs font-medium transition-colors'
								style={{ background: 'var(--nav-hover-bg, rgba(255, 255, 255, 0.6))', color: 'var(--admin-text-secondary, #6b7b79)' }}>
								首页
							</Link>
						}
					/>
				}
				header={<ManageTopbar />}>
				{children}
			</Uiv2AppShell>
		</AuthGate>
	)
}
