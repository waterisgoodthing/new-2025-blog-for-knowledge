import { fileToBase64NoPrefix, hashFileSHA256 } from '@/lib/file-utils'
import type { Blogger } from '../grid-view'
import type { AvatarItem } from '../components/avatar-upload-dialog'
import { getFileExt } from '@/lib/utils'
import { toast } from 'sonner'
import { commitFilesToGithub, type CommitFileItem } from '@/lib/api/sync'

export type PushBloggersParams = {
	bloggers: Blogger[]
	avatarItems?: Map<string, AvatarItem>
}

export async function pushBloggers(params: PushBloggersParams): Promise<void> {
	const { bloggers, avatarItems } = params

	toast.info('正在准备博主列表和头像数据...')

	const files: CommitFileItem[] = []
	const uploadedHashes = new Set<string>()
	let updatedBloggers = [...bloggers]

	// Process avatar uploads
	if (avatarItems && avatarItems.size > 0) {
		for (const [url, avatarItem] of avatarItems.entries()) {
			if (avatarItem.type === 'file') {
				const hash = avatarItem.hash || (await hashFileSHA256(avatarItem.file))
				const ext = getFileExt(avatarItem.file.name)
				const filename = `${hash}${ext}`
				const publicPath = `/images/blogger/${filename}`

				if (!uploadedHashes.has(hash)) {
					const path = `public/images/blogger/${filename}`
					const contentBase64 = await fileToBase64NoPrefix(avatarItem.file)
					files.push({
						path,
						content_base64: contentBase64,
						encoding: 'base64'
					})
					uploadedHashes.add(hash)
				}

				// Update blogger avatar URL
				updatedBloggers = updatedBloggers.map(b => (b.url === url ? { ...b, avatar: publicPath } : b))
			}
		}
	}

	// Create bloggers list.json file
	const bloggersJson = JSON.stringify(updatedBloggers, null, '\t')
	const bloggersJsonBase64 = btoa(unescape(encodeURIComponent(bloggersJson)))
	files.push({
		path: 'src/app/bloggers/list.json',
		content_base64: bloggersJsonBase64,
		encoding: 'base64'
	})

	toast.info('正在向后端推送博主列表更新...')
	const res = await commitFilesToGithub({
		commitMessage: '更新博主列表',
		files
	})

	toast.success(`保存博主列表成功！(提交: ${res.commit_sha.substring(0, 8)})`)
}
