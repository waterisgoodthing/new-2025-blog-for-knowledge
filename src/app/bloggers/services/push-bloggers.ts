import { updateBloggers, uploadContentImage, type BloggerItem } from '@/lib/api/content'
import type { Blogger } from '../grid-view'
import type { AvatarItem } from '../components/avatar-upload-dialog'
import { toast } from 'sonner'

export type PushBloggersParams = {
	bloggers: Blogger[]
	avatarItems?: Map<string, AvatarItem>
}

export async function pushBloggers(params: PushBloggersParams): Promise<void> {
	const { bloggers, avatarItems } = params

	toast.info('正在保存博主列表...')

	let updatedBloggers = [...bloggers]

	if (avatarItems && avatarItems.size > 0) {
		for (const [url, avatarItem] of avatarItems.entries()) {
			if (avatarItem.type === 'file') {
				const result = await uploadContentImage(avatarItem.file, 'blogger')
				updatedBloggers = updatedBloggers.map(b => (b.url === url ? { ...b, avatar: result.url } : b))
			}
		}
	}

	const items: BloggerItem[] = updatedBloggers.map(b => ({
		name: b.name,
		avatar: b.avatar,
		url: b.url,
		description: b.description,
		stars: b.stars || 0,
		status: b.status || 'recent',
	}))

	await updateBloggers(items)
	toast.success('博主列表保存成功！')
}
