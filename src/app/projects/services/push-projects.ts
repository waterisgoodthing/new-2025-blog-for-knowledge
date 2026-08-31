import { updateProjects, uploadContentImage, type ProjectItem } from '@/lib/api/content'
import type { Project } from '../components/project-card'
import type { ImageItem } from '../components/image-upload-dialog'
import { toast } from 'sonner'

export type PushProjectsParams = {
	projects: Project[]
	imageItems?: Map<string, ImageItem>
}

export async function pushProjects(params: PushProjectsParams): Promise<void> {
	const { projects, imageItems } = params

	toast.info('正在保存项目列表...')

	let updatedProjects = [...projects]

	if (imageItems && imageItems.size > 0) {
		for (const [url, imageItem] of imageItems.entries()) {
			if (imageItem.type === 'file') {
				const result = await uploadContentImage(imageItem.file, 'project')
				updatedProjects = updatedProjects.map(p => (p.url === url ? { ...p, image: result.url } : p))
			}
		}
	}

	const items: ProjectItem[] = updatedProjects.map(p => ({
		name: p.name,
		year: p.year,
		description: p.description,
		image: p.image,
		url: p.url,
		tags: p.tags || [],
		github: p.github || null,
		npm: p.npm || null,
	}))

	await updateProjects(items)
	toast.success('项目列表保存成功！')
}
