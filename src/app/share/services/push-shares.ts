import { fileToBase64NoPrefix, hashFileSHA256 } from '@/lib/file-utils'
import type { Share } from '../components/share-card'
import type { LogoItem } from '../components/logo-upload-dialog'
import { getFileExt } from '@/lib/utils'
import { toast } from 'sonner'
import { commitFilesToGithub, type CommitFileItem } from '@/lib/api/sync'

export type PushSharesParams = {
	shares: Share[]
	logoItems?: Map<string, LogoItem>
}

export async function pushShares(params: PushSharesParams): Promise<void> {
	const { shares, logoItems } = params

	toast.info('正在准备分享列表和图标数据...')

	const files: CommitFileItem[] = []
	const uploadedHashes = new Set<string>()
	let updatedShares = [...shares]

	// Process logo uploads
	if (logoItems && logoItems.size > 0) {
		for (const [url, logoItem] of logoItems.entries()) {
			if (logoItem.type === 'file') {
				const hash = logoItem.hash || (await hashFileSHA256(logoItem.file))
				const ext = getFileExt(logoItem.file.name)
				const filename = `${hash}${ext}`
				const publicPath = `/images/share/${filename}`

				if (!uploadedHashes.has(hash)) {
					const path = `public/images/share/${filename}`
					const contentBase64 = await fileToBase64NoPrefix(logoItem.file)
					files.push({
						path,
						content_base64: contentBase64,
						encoding: 'base64'
					})
					uploadedHashes.add(hash)
				}

				// Update share logo URL
				updatedShares = updatedShares.map(s => (s.url === url ? { ...s, logo: publicPath } : s))
			}
		}
	}

	const sharesJson = JSON.stringify(updatedShares, null, '\t')
	const sharesJsonBase64 = btoa(unescape(encodeURIComponent(sharesJson)))
	files.push({
		path: 'src/app/share/list.json',
		content_base64: sharesJsonBase64,
		encoding: 'base64'
	})

	toast.info('正在向后端推送分享列表更新...')
	const res = await commitFilesToGithub({
		commitMessage: '更新分享列表',
		files
	})

	toast.success(`分享列表保存成功！(提交: ${res.commit_sha.substring(0, 8)})`)
}
