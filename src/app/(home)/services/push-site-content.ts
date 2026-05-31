import { fileToBase64NoPrefix } from '@/lib/file-utils'
import { saveConfigToGithub, type UploadFileItem } from '@/lib/api/sync'
import { toast } from 'sonner'
import type { SiteContent, CardStyles } from '../stores/config-store'
import type { FileItem, ArtImageUploads, SocialButtonImageUploads, BackgroundImageUploads } from '../config-dialog/site-settings'

type ArtImageConfig = SiteContent['artImages'][number]
type BackgroundImageConfig = SiteContent['backgroundImages'][number]

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
	toast.info('正在准备站点配置及文件...')

	let syncFavicon: UploadFileItem | null = null
	if (faviconItem?.type === 'file') {
		const base64 = await fileToBase64NoPrefix(faviconItem.file)
		syncFavicon = { content_base64: base64, filename: faviconItem.file.name }
	}

	let syncAvatar: UploadFileItem | null = null
	if (avatarItem?.type === 'file') {
		const base64 = await fileToBase64NoPrefix(avatarItem.file)
		syncAvatar = { content_base64: base64, filename: avatarItem.file.name }
	}

	const syncArtImageUploads: Record<string, UploadFileItem> = {}
	if (artImageUploads) {
		for (const [id, item] of Object.entries(artImageUploads)) {
			if (item.type === 'file') {
				const base64 = await fileToBase64NoPrefix(item.file)
				syncArtImageUploads[id] = { content_base64: base64, filename: item.file.name }
			}
		}
	}

	const syncBackgroundImageUploads: Record<string, UploadFileItem> = {}
	if (backgroundImageUploads) {
		for (const [id, item] of Object.entries(backgroundImageUploads)) {
			if (item.type === 'file') {
				const base64 = await fileToBase64NoPrefix(item.file)
				syncBackgroundImageUploads[id] = { content_base64: base64, filename: item.file.name }
			}
		}
	}

	const syncSocialButtonImageUploads: Record<string, UploadFileItem> = {}
	if (socialButtonImageUploads) {
		for (const [id, item] of Object.entries(socialButtonImageUploads)) {
			if (item.type === 'file') {
				const base64 = await fileToBase64NoPrefix(item.file)
				syncSocialButtonImageUploads[id] = { content_base64: base64, filename: item.file.name }
			}
		}
	}

	const syncRemovedArtImages = removedArtImages?.map(art => ({ id: art.id, url: art.url })) || []
	const syncRemovedBackgroundImages = removedBackgroundImages?.map(bg => ({ id: bg.id, url: bg.url })) || []

	toast.info('正在向后端推送站点配置...')
	const res = await saveConfigToGithub({
		siteContent,
		cardStyles,
		favicon: syncFavicon,
		avatar: syncAvatar,
		artImageUploads: syncArtImageUploads,
		removedArtImages: syncRemovedArtImages,
		backgroundImageUploads: syncBackgroundImageUploads,
		removedBackgroundImages: syncRemovedBackgroundImages,
		socialButtonImageUploads: syncSocialButtonImageUploads
	})

	toast.success(`配置保存成功！(提交: ${res.commit_sha.substring(0, 8)})`)
}
