import { updateShares, uploadContentImage, type ShareItem } from '@/lib/api/content'
import type { Share } from '../components/share-card'
import type { LogoItem } from '../components/logo-upload-dialog'
import { toast } from 'sonner'

export type PushSharesParams = {
	shares: Share[]
	logoItems?: Map<string, LogoItem>
}

export async function pushShares(params: PushSharesParams): Promise<void> {
	const { shares, logoItems } = params

	toast.info('正在保存分享列表...')

	let updatedShares = [...shares]

	if (logoItems && logoItems.size > 0) {
		for (const [url, logoItem] of logoItems.entries()) {
			if (logoItem.type === 'file') {
				const result = await uploadContentImage(logoItem.file, 'share')
				updatedShares = updatedShares.map(s => (s.url === url ? { ...s, logo: result.url } : s))
			}
		}
	}

	const items: ShareItem[] = updatedShares.map(s => ({
		name: s.name,
		logo: s.logo,
		url: s.url,
		description: s.description,
		tags: s.tags || [],
		stars: s.stars || 0,
	}))

	await updateShares(items)
	toast.success('分享列表保存成功！')
}
