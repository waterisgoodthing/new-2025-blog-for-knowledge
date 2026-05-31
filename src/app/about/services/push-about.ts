import { saveJsonFileToGithub } from '@/lib/api/sync'
import { toast } from 'sonner'

export type AboutData = {
	title: string
	description: string
	content: string
}

export async function pushAbout(data: AboutData): Promise<void> {
	toast.info('正在向后端推送关于页面修改...')
	const res = await saveJsonFileToGithub({
		path: 'src/app/about/list.json',
		content: data,
		commitMessage: '更新关于页面'
	})
	toast.success(`关于页面保存成功！(提交: ${res.commit_sha.substring(0, 8)})`)
}
