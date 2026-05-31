import { saveJsonFileToGithub } from '@/lib/api/sync'
import { toast } from 'sonner'

export type PushSnippetsParams = {
	snippets: string[]
}

export async function pushSnippets(params: PushSnippetsParams): Promise<void> {
	const { snippets } = params

	toast.info('正在向后端推送句子列表更新...')
	const res = await saveJsonFileToGithub({
		path: 'src/app/snippets/list.json',
		content: snippets,
		commitMessage: '更新句子列表'
	})

	toast.success(`句子列表保存成功！(提交: ${res.commit_sha.substring(0, 8)})`)
}
