import { create } from 'zustand'
import siteContent from '@/config/site-content.json'
import cardStyles from '@/config/card-styles.json'

export type SocialButtonType =
	| 'github'
	| 'juejin'
	| 'email'
	| 'link'
	| 'x'
	| 'tg'
	| 'wechat'
	| 'facebook'
	| 'tiktok'
	| 'instagram'
	| 'weibo'
	| 'xiaohongshu'
	| 'zhihu'
	| 'bilibili'
	| 'qq'

export interface SiteContent {
	meta: {
		title: string
		description: string
		username: string
	}
	theme: {
		colorBrand: string
		colorPrimary: string
		colorSecondary: string
		colorBrandSecondary: string
		colorBg: string
		colorBorder: string
		colorCard: string
		colorArticle: string
	}
	backgroundColors: string[]
	artImages: Array<{ id: string; url: string }>
	currentArtImageId: string
	backgroundImages: Array<{ id: string; url: string }>
	currentBackgroundImageId: string
	socialButtons: Array<{ id: string; type: SocialButtonType; value: string; label?: string; order: number }>
	clockShowSeconds: boolean
	summaryInContent: boolean
	isCachePem: boolean
	hideEditButton: boolean
	enableCategories: boolean
	currentHatIndex: number
	hatFlipped: boolean
	enableChristmas: boolean
	beian: {
		text: string
		link: string
	}
	faviconUrl?: string
	avatarUrl?: string
}

export type CardStyles = typeof cardStyles

const initialSiteContent = siteContent as SiteContent

interface ConfigStore {
	siteContent: SiteContent
	cardStyles: CardStyles
	regenerateKey: number
	configDialogOpen: boolean
	setSiteContent: (content: SiteContent) => void
	setCardStyles: (styles: CardStyles) => void
	resetSiteContent: () => void
	resetCardStyles: () => void
	regenerateBubbles: () => void
	setConfigDialogOpen: (open: boolean) => void
}

export const useConfigStore = create<ConfigStore>((set, get) => ({
	siteContent: { ...initialSiteContent },
	cardStyles: { ...cardStyles },
	regenerateKey: 0,
	configDialogOpen: false,
	setSiteContent: (content: SiteContent) => {
		set({ siteContent: content })
	},
	setCardStyles: (styles: CardStyles) => {
		set({ cardStyles: styles })
	},
	resetSiteContent: () => {
		set({ siteContent: { ...initialSiteContent } })
	},
	resetCardStyles: () => {
		set({ cardStyles: { ...cardStyles } })
	},
	regenerateBubbles: () => {
		set(state => ({ regenerateKey: state.regenerateKey + 1 }))
	},
	setConfigDialogOpen: (open: boolean) => {
		set({ configDialogOpen: open })
	}
}))
