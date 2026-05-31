import { fileToBase64NoPrefix, hashFileSHA256 } from '@/lib/file-utils'
import type { ImageItem } from '../../projects/components/image-upload-dialog'
import { getFileExt } from '@/lib/utils'
import { toast } from 'sonner'
import type { Picture } from '../page'
import { commitFilesToGithub, type CommitFileItem } from '@/lib/api/sync'

export type PushPicturesParams = {
	pictures: Picture[]
	originalPictures: Picture[]
	imageItems?: Map<string, ImageItem>
}

export async function pushPictures(params: PushPicturesParams): Promise<void> {
	const { pictures, originalPictures, imageItems } = params

	toast.info('正在准备图床更新数据...')

	const files: CommitFileItem[] = []
	const uploadedHashes = new Set<string>()
	let updatedPictures = [...pictures]

	// Process image file uploads
	if (imageItems && imageItems.size > 0) {
		toast.info('正在准备图片上传文件...')
		for (const [key, imageItem] of imageItems.entries()) {
			if (imageItem.type === 'file') {
				const hash = imageItem.hash || (await hashFileSHA256(imageItem.file))
				const ext = getFileExt(imageItem.file.name)
				const filename = `${hash}${ext}`
				const publicPath = `/images/pictures/${filename}`

				if (!uploadedHashes.has(hash)) {
					const path = `public/images/pictures/${filename}`
					const contentBase64 = await fileToBase64NoPrefix(imageItem.file)
					files.push({
						path,
						content_base64: contentBase64,
						encoding: 'base64'
					})
					uploadedHashes.add(hash)
				}

				const [groupId, indexStr] = key.split('::')
				const imageIndex = Number(indexStr) || 0

				updatedPictures = updatedPictures.map(p => {
					if (p.id !== groupId) return p

					const currentImages = p.images && p.images.length > 0 ? p.images : p.image ? [p.image] : []
					const nextImages = currentImages.map((img, idx) => (idx === imageIndex ? publicPath : img))

					return {
						...p,
						image: undefined,
						images: nextImages
					}
				})
			}
		}
	}

	// 收集当前所有使用的图片 URL
	const currentImageUrls = new Set<string>()
	for (const picture of updatedPictures) {
		if (picture.image) {
			currentImageUrls.add(picture.image)
		}
		if (picture.images && picture.images.length > 0) {
			picture.images.forEach(url => currentImageUrls.add(url))
		}
	}

	// 找出不再使用的图片并将其删除
	toast.info('正在检查需要删除的图片文件...')
	const previousImageUrls = new Set<string>()
	for (const picture of originalPictures) {
		if (picture.image) {
			previousImageUrls.add(picture.image)
		}
		if (picture.images && picture.images.length > 0) {
			picture.images.forEach(url => previousImageUrls.add(url))
		}
	}

	// 找出不再使用的图片 URL
	for (const url of previousImageUrls) {
		if (!currentImageUrls.has(url) && url.startsWith('/images/pictures/')) {
			const filename = url.replace('/images/pictures/', '')
			const path = `public/images/pictures/${filename}`
			files.push({
				path,
				content_base64: null // null means delete
			})
		}
	}

	// Serialize and add pictures list.json
	const picturesJson = JSON.stringify(updatedPictures, null, '\t')
	const picturesJsonBase64 = btoa(unescape(encodeURIComponent(picturesJson)))
	files.push({
		path: 'src/app/pictures/list.json',
		content_base64: picturesJsonBase64,
		encoding: 'base64'
	})

	toast.info('正在向后端推送图床更新...')
	const res = await commitFilesToGithub({
		commitMessage: '更新图床列表',
		files
	})

	toast.success(`图床列表更新成功！(提交: ${res.commit_sha.substring(0, 8)})`)
}
