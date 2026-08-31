import { updateSiteSettings, uploadContentImage, deleteContentImage, type SiteSettingsPayload } from '@/lib/api/content'
import { toast } from 'sonner'
import type { SiteContent, CardStyles } from '../stores/config-store'
import type { FileItem, ArtImageUploads, SocialButtonImageUploads, BackgroundImageUploads } from '../config-dialog/site-settings'

type ArtImageConfig = SiteContent['artImages'][number]
type BackgroundImageConfig = SiteContent['backgroundImages'][number]

async function uploadIfFile(item: FileItem | null | undefined, scope: string): Promise<string | null> {
	if (!item || item.type !== 'file') return null
	const result = await uploadContentImage(item.file, scope)
	return result.url
}

export async function pushSiteContent(
	siteContent: SiteContent,
	cardStyles: CardStyles,
	faviconItem?: FileItem | null,
	avatarItem?: FileItem | null,
	artImageUploads?: ArtImageUploads,
	removedArtImages?: ArtImageConfig[],
	backgroundImageUploads?: BackgroundImageUploads,
	removedBackgroundImages?: BackgroundImageConfig[],
	socialButtonImageUploads?: SocialButtonImageUploads
): Promise<void> {
	toast.info('正在保存站点配置...')

	let currentSiteContent = { ...siteContent }

	if (faviconItem?.type === 'file') {
		const url = await uploadIfFile(faviconItem, 'site')
		if (url) currentSiteContent.faviconUrl = url
	}

	if (avatarItem?.type === 'file') {
		const url = await uploadIfFile(avatarItem, 'site')
		if (url) currentSiteContent.avatarUrl = url
	}

	if (artImageUploads) {
		for (const [id, item] of Object.entries(artImageUploads)) {
			if (item.type === 'file') {
				const result = await uploadContentImage(item.file, 'site')
				currentSiteContent = {
					...currentSiteContent,
					artImages: currentSiteContent.artImages.map(art =>
						art.id === id ? { ...art, url: result.url } : art
					),
				}
			}
		}
	}

	if (removedArtImages) {
		for (const art of removedArtImages) {
			await deleteContentImage(art.url).catch(() => {})
		}
	}

	if (backgroundImageUploads) {
		for (const [id, item] of Object.entries(backgroundImageUploads)) {
			if (item.type === 'file') {
				const result = await uploadContentImage(item.file, 'site')
				currentSiteContent = {
					...currentSiteContent,
					backgroundImages: currentSiteContent.backgroundImages.map(bg =>
						bg.id === id ? { ...bg, url: result.url } : bg
					),
				}
			}
		}
	}

	if (removedBackgroundImages) {
		for (const bg of removedBackgroundImages) {
			await deleteContentImage(bg.url).catch(() => {})
		}
	}

	if (socialButtonImageUploads) {
		for (const [id, item] of Object.entries(socialButtonImageUploads)) {
			if (item.type === 'file') {
				const result = await uploadContentImage(item.file, 'site')
				currentSiteContent = {
					...currentSiteContent,
					socialButtons: currentSiteContent.socialButtons.map(btn =>
						btn.id === id ? { ...btn, value: result.url } : btn
					),
				}
			}
		}
	}

	const payload: SiteSettingsPayload = {
		siteContent: currentSiteContent as SiteSettingsPayload['siteContent'],
		cardStyles: cardStyles as Record<string, unknown>,
	}

	await updateSiteSettings(payload)
	toast.success('站点配置保存成功！')
}
