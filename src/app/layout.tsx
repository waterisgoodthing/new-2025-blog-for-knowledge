import '@/styles/globals.css'

import type { Metadata } from 'next'
import Layout from '@/layout'
import Head from '@/layout/head'
import siteContent from '@/config/site-content.json'

const {
	meta: { title, description },
	theme
} = siteContent

export const metadata: Metadata = {
	title,
	description,
	openGraph: {
		title,
		description
	},
	twitter: {
		title,
		description
	}
}

const themeConfig = theme as Record<string, string | undefined>

/**
 * Legacy -> UI V2 bridge.
 *
 * IMPORTANT: do NOT give the dual-surface tokens a hardcoded `|| '#fallback'`.
 * Inline custom properties on `<html>` outrank *any* stylesheet rule, including
 * `[data-theme='dark']` in ui-v2/tokens.css — a fallback here would pin the
 * light palette and make dark mode unreachable. `undefined` values are skipped
 * by React, so an unconfigured key simply falls through to the CSS defaults.
 * Runtime configurability is preserved for whoever adds these keys to
 * site-content.json.
 */
const htmlStyle: React.CSSProperties & Record<string, string | undefined> = {
	// 桥接 Brand 色（缺省由 tokens.css 提供 #3db8a8）
	'--brand': themeConfig.brand,
	// 桥接 Editorial（新增）
	'--editorial-bg': themeConfig.editorialBg,
	'--editorial-surface': themeConfig.editorialSurface,
	'--editorial-text-primary': themeConfig.editorialTextPrimary,
	'--editorial-text-secondary': themeConfig.editorialTextSecondary,
	'--editorial-accent': themeConfig.editorialAccent,
	// 桥接 Admin（新增）
	'--admin-text-primary': themeConfig.adminTextPrimary,
	'--admin-text-secondary': themeConfig.adminTextSecondary,
	// 保留其他 Legacy Token 向后兼容
	'--color-primary': themeConfig.colorPrimary,
	'--color-secondary': themeConfig.colorSecondary,
	'--color-brand': themeConfig.colorBrand,
	'--color-brand-secondary': themeConfig.colorBrandSecondary,
	'--color-bg': themeConfig.colorBg,
	'--color-border': themeConfig.colorBorder,
	'--color-card': themeConfig.colorCard,
	'--color-article': themeConfig.colorArticle
}

export default async function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
	return (
		<html lang='zh-CN' data-scroll-behavior='smooth' suppressHydrationWarning style={htmlStyle}>
			<Head />

			<body>
				<script
					dangerouslySetInnerHTML={{
						__html: `
					if (/windows|win32/i.test(navigator.userAgent)) {
						document.documentElement.classList.add('windows');
					}
		      `
					}}
				/>

				<Layout>{children}</Layout>
			</body>
		</html>
	)
}
