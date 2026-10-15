import type { ReactNode } from 'react'
import { UIV2_NAV_SECTIONS } from './navigation'

export interface Uiv2AppSidebarProps {
	/** Current path used to mark the active entry (aria-current="page"). */
	currentPath: string
}

const LINK_BASE =
	'flex min-h-[40px] items-center rounded-[var(--uiv2-radius-sm)] px-3 py-2 text-[var(--uiv2-text-sm)] ' +
	'text-[var(--uiv2-text-secondary)] transition-colors duration-[var(--uiv2-duration-normal)] ' +
	'hover:bg-white/70 hover:text-[var(--uiv2-text-primary)] ' +
	'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]'

/** Presentational desktop sidebar (U1). Data-free: sections come from navigation.ts. */
export function Uiv2AppSidebar({ currentPath }: Uiv2AppSidebarProps) {
	return (
		<nav
			aria-label="学习系统导航"
			className="hidden w-60 shrink-0 flex-col gap-6 md:flex"
		>
			{UIV2_NAV_SECTIONS.map(section => (
				<section key={section.id} aria-labelledby={`uiv2-nav-${section.id}`}>
					<h2
						id={`uiv2-nav-${section.id}`}
						className="px-3 pb-2 text-[var(--uiv2-text-xs)] font-medium tracking-wide text-[var(--uiv2-text-secondary)]"
					>
						{section.label}
					</h2>
					<ul className="flex flex-col gap-1">
						{section.items.map(item => {
							const active = item.href === currentPath
							return (
								<li key={item.key}>
									<a
										href={item.href}
										aria-current={active ? 'page' : undefined}
										className={
											LINK_BASE +
											(active
												? ' bg-white/80 font-medium text-[var(--uiv2-text-primary)]'
												: ' font-normal')
										}
									>
										{item.label}
									</a>
								</li>
							)
						})}
					</ul>
				</section>
			))}
		</nav>
	)
}

export interface Uiv2MobileNavProps {
	currentPath: string
}

/** Presentational mobile navigation (U1). Compact horizontal list, keyboard-native anchors. */
export function Uiv2MobileNav({ currentPath }: Uiv2MobileNavProps) {
	return (
		<nav aria-label="移动导航" className="md:hidden">
			<ul className="flex gap-2 overflow-x-auto pb-2">
				{UIV2_NAV_SECTIONS.flatMap(section =>
					section.items.map(item => {
						const active = item.href === currentPath
						return (
							<li key={`${section.id}-${item.key}`} className="shrink-0">
								<a
									href={item.href}
									aria-current={active ? 'page' : undefined}
									className={
										'flex min-h-[40px] items-center rounded-[var(--uiv2-radius-full)] border px-4 text-[var(--uiv2-text-sm)] ' +
										'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)] ' +
										(active
											? 'border-transparent bg-[var(--uiv2-brand-ink)] font-medium text-white'
											: 'border-[var(--uiv2-border)] bg-white/60 text-[var(--uiv2-text-secondary)]')
									}
								>
									{item.label}
								</a>
							</li>
						)
					}),
				)}
			</ul>
		</nav>
	)
}

export interface Uiv2BreadcrumbProps {
	currentPath: string
}

/** Presentational breadcrumb: 首页 / Section / Item (U1). Unknown paths degrade to 首页 only. */
export function Uiv2Breadcrumb({ currentPath }: Uiv2BreadcrumbProps) {
	const trail: Array<{ label: string; href?: string }> = [{ label: '首页', href: '/' }]
	for (const section of UIV2_NAV_SECTIONS) {
		const item = section.items.find(entry => entry.href === currentPath)
		if (item) {
			if (section.id !== 'home') trail.push({ label: section.label })
			if (item.key !== 'home') trail.push({ label: item.label })
			break
		}
	}
	return (
		<nav aria-label="面包屑">
			<ol className="flex flex-wrap items-center gap-2 text-[var(--uiv2-text-sm)]">
				{trail.map((crumb, index) => {
					const last = index === trail.length - 1
					return (
						<li key={`${crumb.label}-${index}`} className="flex items-center gap-2">
							{index > 0 ? (
								<span aria-hidden="true" className="text-[var(--uiv2-text-secondary)]">
									/
								</span>
							) : null}
							{crumb.href && !last ? (
								<a
									href={crumb.href}
									className="text-[var(--uiv2-text-secondary)] underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]"
								>
									{crumb.label}
								</a>
							) : (
								<span aria-current={last ? 'page' : undefined} className="text-[var(--uiv2-text-primary)]">
									{crumb.label}
								</span>
							)}
						</li>
					)
				})}
			</ol>
		</nav>
	)
}

export interface Uiv2AppHeaderProps {
	currentPath: string
	/** Primary action slot (e.g. “新建题目”). Rendered only when provided. */
	action?: ReactNode
}

/** Presentational header with location context (U1). */
export function Uiv2AppHeader({ currentPath, action }: Uiv2AppHeaderProps) {
	let sectionLabel = '学习系统'
	let itemLabel = '未知位置'
	for (const section of UIV2_NAV_SECTIONS) {
		const item = section.items.find(entry => entry.href === currentPath)
		if (item) {
			sectionLabel = section.label
			itemLabel = item.label
			break
		}
	}
	return (
		<header className="flex flex-wrap items-center justify-between gap-3">
			<div className="min-w-0">
				<p className="text-[var(--uiv2-text-xs)] font-medium tracking-wide text-[var(--uiv2-text-secondary)]">
					{sectionLabel}
				</p>
				<h1 className="truncate text-[var(--uiv2-text-xl)] font-semibold text-[var(--uiv2-text-primary)]">
					{itemLabel}
				</h1>
			</div>
			{action ? <div className="flex shrink-0 items-center gap-2">{action}</div> : null}
		</header>
	)
}

export interface Uiv2PageLayoutProps {
	children: ReactNode
	/** Narrow reading width for detail pages; default wide for workspace lists. */
	width?: 'wide' | 'narrow'
}

/** Presentational content container (U1). Medium density, max width, no overflow. */
export function Uiv2PageLayout({ children, width = 'wide' }: Uiv2PageLayoutProps) {
	return (
		<div
			className={
				'mx-auto w-full min-w-0 ' + (width === 'narrow' ? 'max-w-[840px]' : 'max-w-7xl')
			}
		>
			{children}
		</div>
	)
}

export interface Uiv2AppShellProps {
	currentPath: string
	headerAction?: ReactNode
	children: ReactNode
}

/** Presentational app shell (U1): sidebar + header + breadcrumb + main + mobile nav. */
export function Uiv2AppShell({ currentPath, headerAction, children }: Uiv2AppShellProps) {
	return (
		<div className="min-h-screen min-w-0 bg-[var(--uiv2-surface)] px-4 py-6 sm:px-6 md:py-8">
			<Uiv2PageLayout>
				<div className="flex flex-col gap-4 md:flex-row md:gap-6">
					<Uiv2AppSidebar currentPath={currentPath} />
					<section className="w-full min-w-0 flex-1 overflow-hidden rounded-[var(--uiv2-radius-lg)] border border-[var(--uiv2-border)] bg-white/70 p-5 shadow-[var(--uiv2-shadow-md)] sm:p-7">
						<Uiv2MobileNav currentPath={currentPath} />
						<Uiv2AppHeader currentPath={currentPath} action={headerAction} />
						<div className="pt-3">
							<Uiv2Breadcrumb currentPath={currentPath} />
						</div>
						<main className="min-w-0 pt-4">{children}</main>
					</section>
				</div>
			</Uiv2PageLayout>
		</div>
	)
}
