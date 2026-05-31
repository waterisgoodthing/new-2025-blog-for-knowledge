import { fileToBase64NoPrefix, hashFileSHA256 } from '@/lib/file-utils'
import type { Project } from '../components/project-card'
import type { ImageItem } from '../components/image-upload-dialog'
import { getFileExt } from '@/lib/utils'
import { toast } from 'sonner'
import { commitFilesToGithub, type CommitFileItem } from '@/lib/api/sync'

export type PushProjectsParams = {
	projects: Project[]
	imageItems?: Map<string, ImageItem>
}

export async function pushProjects(params: PushProjectsParams): Promise<void> {
	const { projects, imageItems } = params

	toast.info('正在准备项目列表和图片数据...')

	const files: CommitFileItem[] = []
	const uploadedHashes = new Set<string>()
	let updatedProjects = [...projects]

	if (imageItems && imageItems.size > 0) {
		for (const [url, imageItem] of imageItems.entries()) {
			if (imageItem.type === 'file') {
				const hash = imageItem.hash || (await hashFileSHA256(imageItem.file))
				const ext = getFileExt(imageItem.file.name)
				const filename = `${hash}${ext}`
				const publicPath = `/images/project/${filename}`

				if (!uploadedHashes.has(hash)) {
					const path = `public/images/project/${filename}`
					const contentBase64 = await fileToBase64NoPrefix(imageItem.file)
					files.push({
						path,
						content_base64: contentBase64,
						encoding: 'base64'
					})
					uploadedHashes.add(hash)
				}

				updatedProjects = updatedProjects.map(p => (p.url === url ? { ...p, image: publicPath } : p))
			}
		}
	}

	const projectsJson = JSON.stringify(updatedProjects, null, '\t')
	const projectsJsonBase64 = btoa(unescape(encodeURIComponent(projectsJson)))
	files.push({
		path: 'src/app/projects/list.json',
		content_base64: projectsJsonBase64,
		encoding: 'base64'
	})

	toast.info('正在向后端推送项目列表更新...')
	const res = await commitFilesToGithub({
		commitMessage: '更新项目列表',
		files
	})

	toast.success(`项目列表保存成功！(提交: ${res.commit_sha.substring(0, 8)})`)
}
