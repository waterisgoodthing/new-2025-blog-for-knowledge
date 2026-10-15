import { updateAbout, type AboutContent } from '@/lib/api/content'
import { toast } from 'sonner'

export type AboutData = AboutContent

export async function pushAbout(data: AboutData): Promise<void> {
	toast.info('正在保存关于页面...')
	await updateAbout(data)
	toast.success('关于页面保存成功！')
}
