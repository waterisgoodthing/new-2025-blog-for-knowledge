import { updateSnippets } from '@/lib/api/content'
import { toast } from 'sonner'

export type PushSnippetsParams = {
	snippets: string[]
}

export async function pushSnippets(params: PushSnippetsParams): Promise<void> {
	const { snippets } = params

	toast.info('正在保存句子列表...')
	await updateSnippets(snippets)
	toast.success('句子列表保存成功！')
}
