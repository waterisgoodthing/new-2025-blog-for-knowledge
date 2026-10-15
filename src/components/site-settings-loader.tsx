'use client'

import { useEffect, useRef } from 'react'
import { useConfigStore } from '@/app/(home)/stores/config-store'
import { getSiteSettings } from '@/lib/api/content'
import type { SiteContent, CardStyles } from '@/app/(home)/stores/config-store'

function applyThemeVariables(theme: SiteContent['theme']) {
	if (typeof document === 'undefined' || !theme) return
	const root = document.documentElement
	if (theme.colorBrand) root.style.setProperty('--color-brand', theme.colorBrand)
	if (theme.colorBrandSecondary) root.style.setProperty('--color-brand-secondary', theme.colorBrandSecondary)
	if (theme.colorPrimary) root.style.setProperty('--color-primary', theme.colorPrimary)
	if (theme.colorSecondary) root.style.setProperty('--color-secondary', theme.colorSecondary)
	if (theme.colorBg) root.style.setProperty('--color-bg', theme.colorBg)
	if (theme.colorBorder) root.style.setProperty('--color-border', theme.colorBorder)
	if (theme.colorCard) root.style.setProperty('--color-card', theme.colorCard)
	if (theme.colorArticle) root.style.setProperty('--color-article', theme.colorArticle)
}

function applyFavicon(url: string | null | undefined) {
	if (typeof document === 'undefined') return
	const href = url || '/favicon.png'
	let link = document.querySelector<HTMLLinkElement>('link[rel="icon"]')
	if (!link) {
		link = document.createElement('link')
		link.rel = 'icon'
		document.head.appendChild(link)
	}
	if (link.href !== new URL(href, window.location.origin).href) {
		link.href = href
	}
}

export function SiteSettingsLoader() {
	const { setSiteContent, setCardStyles } = useConfigStore()
	const loaded = useRef(false)

	useEffect(() => {
		if (loaded.current) return
		loaded.current = true

		getSiteSettings()
			.then(data => {
				const sc = data.siteContent as unknown as SiteContent
				const cs = data.cardStyles as CardStyles
				setSiteContent(sc)
				setCardStyles(cs)
				if (sc.theme) applyThemeVariables(sc.theme)
				applyFavicon(sc.faviconUrl)
				if (typeof document !== 'undefined' && sc.meta?.title) {
					document.title = sc.meta.title
				}
			})
			.catch(err => {
				console.error('SiteSettingsLoader: failed to load site settings', err)
			})
	}, [setSiteContent, setCardStyles])

	return null
}
