'use client'

import { usePathname } from 'next/navigation'

import { AuthGate } from '@/components/auth-gate'
import { MobileDrawer, PUBLIC_NAV_GROUPS, PublicTopNav } from '@/components/ui-v2'

const SCROLL_BLOCKS = Array.from({ length: 12 }, (_, index) => index)

/**
 * Phase 3 navigation preview (VSC-09 / VSC-11).
 *
 * Public navigation only: no administrator entry is rendered here (that belongs
 * to the F4 range). Scroll to see floating → sticky, use pointer or keyboard on
 * a disclosure, and narrow the viewport for the mobile drawer.
 */
export default function DevNavPage() {
	return (
		<AuthGate>
			<DevNavContent />
		</AuthGate>
	)
}

function DevNavContent() {
	const pathname = usePathname()
	const currentPath = pathname === '/dev/nav' ? '/' : pathname

	return (
		<div data-surface='editorial' className='min-h-screen' style={{ background: 'var(--editorial-bg)', color: 'var(--editorial-text-primary)' }}>
			<PublicTopNav currentPath={currentPath} brandLabel='UI V2 Navigation' />

			<div className='pt-20 md:pt-24'>
				<MobileDrawer groups={PUBLIC_NAV_GROUPS} currentPath={currentPath} drawerLabel='公开导航' />

				<main className='mx-auto max-w-3xl px-4 pb-16'>
					<h1 className='text-2xl font-bold tracking-tight'>Phase 3 · Navigation 检验台</h1>
					<p className='mt-2 text-sm' style={{ color: 'var(--editorial-text-secondary)' }}>
						上方导航初始为悬浮态；向下滚动约 48px 后切换为 sticky 玻璃条（回到 40px 以下才恢复，避免抖动）。用 Tab / Enter / ↑↓ / Esc 验证下拉菜单。
					</p>

					<ul className='mt-6 space-y-2 text-sm' style={{ color: 'var(--editorial-text-secondary)' }}>
						<li>· Dropdown：点击 / Enter / Space 打开，↑↓ 与 Home/End 移动，Esc 关闭并归还焦点。</li>
						<li>· 外部点击关闭；同一时间只打开一个面板。</li>
						<li>· 不支持 `backdrop-filter` 的浏览器降级为 95% 实色背景。</li>
						<li>· 视口窄于 768px 时，顶部会出现 MobileDrawer 的入口（右侧滑入）。</li>
					</ul>

					<div className='mt-10 space-y-6'>
						{SCROLL_BLOCKS.map(index => (
							<section
								key={index}
								className='rounded-2xl border p-5'
								style={{ background: 'var(--editorial-surface)', borderColor: 'var(--editorial-border)' }}>
								<h2 className='text-sm font-semibold'>滚动观测区块 {index + 1}</h2>
								<p className='mt-1 text-xs' style={{ color: 'var(--editorial-text-secondary)' }}>
									约定：滚动后导航条保持 56px 高度并启用 backdrop blur，内容在其下方滚动。
								</p>
							</section>
						))}
					</div>
				</main>
			</div>
		</div>
	)
}
