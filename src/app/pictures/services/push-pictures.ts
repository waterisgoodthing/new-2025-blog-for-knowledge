import { updatePictures, uploadContentImage, deleteContentImage, type PictureItem } from '@/lib/api/content'
import type { ImageItem } from '../../projects/components/image-upload-dialog'
import { toast } from 'sonner'
import type { Picture } from '../page'

export type PushPicturesParams = {
	pictures: Picture[]
	originalPictures: Picture[]
	imageItems?: Map<string, ImageItem>
}

export async function pushPictures(params: PushPicturesParams): Promise<void> {
	const { pictures, originalPictures, imageItems } = params

	toast.info('正在保存图床列表...')

	let updatedPictures = [...pictures]

	if (imageItems && imageItems.size > 0) {
		for (const [key, imageItem] of imageItems.entries()) {
			if (imageItem.type === 'file') {
				const result = await uploadContentImage(imageItem.file, 'pictures')

				const [groupId, indexStr] = key.split('::')
				const imageIndex = Number(indexStr) || 0

				updatedPictures = updatedPictures.map(p => {
					if (p.id !== groupId) return p

					const currentImages = p.images && p.images.length > 0 ? p.images : p.image ? [p.image] : []
					const nextImages = currentImages.map((img, idx) => (idx === imageIndex ? result.url : img))

					return {
						...p,
						image: undefined,
						images: nextImages,
					}
				})
			}
		}
	}

	const currentImageUrls = new Set<string>()
	for (const picture of updatedPictures) {
		if (picture.image) currentImageUrls.add(picture.image)
		if (picture.images && picture.images.length > 0) {
			picture.images.forEach(url => currentImageUrls.add(url))
		}
	}

	for (const picture of originalPictures) {
		const urls = [picture.image, ...(picture.images || [])].filter(Boolean) as string[]
		for (const url of urls) {
			if (!currentImageUrls.has(url) && url.includes('/images/pictures/')) {
				await deleteContentImage(url).catch(() => {})
			}
		}
	}

	const items: PictureItem[] = updatedPictures.map(p => ({
		id: p.id,
		uploadedAt: p.uploadedAt,
		description: p.description || null,
		image: p.image || null,
		images: p.images || null,
	}))

	await updatePictures(items)
	toast.success('图床列表保存成功！')
}
