import { useCallback } from 'react'
import { toast } from 'sonner'
import { useRouter } from 'next/navigation'
import { pushBlog } from '../services/push-blog'
import { deleteBlog } from '../services/delete-blog'
import { useWriteStore } from '../stores/write-store'
import { getContentDetailHref, getContentListHref } from '@/lib/content-routes'

export function usePublish() {
	const { loading, setLoading, form, cover, images, mode, originalSlug } = useWriteStore()
	const router = useRouter()

	const onPublish = useCallback(async () => {
		try {
			setLoading(true)
			await pushBlog({
				form,
				cover,
				images,
				mode,
				originalSlug
			})

			const successMsg = mode === 'edit' ? '更新成功' : '发布成功'
			toast.success(successMsg)
			router.push(getContentDetailHref('blog', originalSlug || form.slug))
		} catch (err: any) {
			console.error(err)
			toast.error(err?.message || '操作失败')
		} finally {
			setLoading(false)
		}
	}, [form, cover, images, mode, originalSlug, router, setLoading])

	const onDelete = useCallback(async () => {
		const targetSlug = originalSlug || form.slug
		if (!targetSlug) {
			toast.error('缺少 slug，无法删除')
			return
		}
		try {
			setLoading(true)
			await deleteBlog(targetSlug)
			toast.success('删除成功')
			router.push(getContentListHref('blog'))
		} catch (err: any) {
			console.error(err)
			toast.error(err?.message || '删除失败')
		} finally {
			setLoading(false)
		}
	}, [form.slug, originalSlug, router, setLoading])

	return {
		loading,
		onPublish,
		onDelete
	}
}
