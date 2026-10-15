'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'motion/react'
import { toast } from 'sonner'
import GridView from './grid-view'
import CreateDialog from './components/create-dialog'
import { pushShares } from './services/push-shares'
import { useAdminAuth } from '@/hooks/use-admin-auth'
import { useConfigStore } from '@/app/(home)/stores/config-store'
import { getShares } from '@/lib/api/content'
import type { Share } from './components/share-card'
import type { LogoItem } from './components/logo-upload-dialog'

export default function Page() {
	const router = useRouter()
	const { isAdmin, isLoading: authLoading } = useAdminAuth({ mode: 'optional' })
	const [shares, setShares] = useState<Share[]>([])
	const [originalShares, setOriginalShares] = useState<Share[]>([])
	const [isEditMode, setIsEditMode] = useState(false)
	const [isSaving, setIsSaving] = useState(false)
	const [editingShare, setEditingShare] = useState<Share | null>(null)
	const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
	const [logoItems, setLogoItems] = useState<Map<string, LogoItem>>(new Map())
	const [isLoading, setIsLoading] = useState(true)
	const { siteContent } = useConfigStore()
	const hideEditButton = siteContent.hideEditButton ?? false

	useEffect(() => {
		if (!authLoading && !isAdmin) {
			router.replace('/discover?tab=shares')
		}
	}, [authLoading, isAdmin, router])

	useEffect(() => {
		getShares()
			.then(data => {
				setShares(data as Share[])
				setOriginalShares(data as Share[])
			})
			.catch(err => {
				console.error('Failed to load shares:', err)
				toast.error('加载分享列表失败')
			})
			.finally(() => setIsLoading(false))
	}, [])

	const handleUpdate = (updatedShare: Share, oldShare: Share, logoItem?: LogoItem) => {
		setShares(prev => prev.map(s => (s.url === oldShare.url ? updatedShare : s)))
		if (logoItem) {
			setLogoItems(prev => {
				const newMap = new Map(prev)
				newMap.set(updatedShare.url, logoItem)
				return newMap
			})
		}
	}

	const handleAdd = () => {
		setEditingShare(null)
		setIsCreateDialogOpen(true)
	}

	const handleSaveShare = (updatedShare: Share) => {
		if (editingShare) {
			const updated = shares.map(s => (s.url === editingShare.url ? updatedShare : s))
			setShares(updated)
		} else {
			setShares([...shares, updatedShare])
		}
	}

	const handleDelete = (share: Share) => {
		if (confirm(`确定要删除 ${share.name} 吗？`)) {
			setShares(shares.filter(s => s.url !== share.url))
		}
	}

	const handleSaveClick = () => {
		handleSave()
	}

	const handleSave = async () => {
		setIsSaving(true)

		try {
			await pushShares({
				shares,
				logoItems
			})

			setOriginalShares(shares)
			setLogoItems(new Map())
			setIsEditMode(false)
			toast.success('保存成功！')
		} catch (error: any) {
			console.error('Failed to save:', error)
			toast.error(`保存失败: ${error?.message || '未知错误'}`)
		} finally {
			setIsSaving(false)
		}
	}

	const handleCancel = () => {
		setShares(originalShares)
		setLogoItems(new Map())
		setIsEditMode(false)
	}

	const buttonText = '保存'

	useEffect(() => {
		const handleKeyDown = (e: KeyboardEvent) => {
			if (isAdmin && !isEditMode && (e.ctrlKey || e.metaKey) && e.key === ',') {
				e.preventDefault()
				setIsEditMode(true)
			}
		}

		window.addEventListener('keydown', handleKeyDown)
		return () => {
			window.removeEventListener('keydown', handleKeyDown)
		}
	}, [isAdmin, isEditMode])

	if (authLoading || (!isAdmin && !isLoading)) {
		return (
			<div className='flex min-h-[70vh] items-center justify-center'>
				<div className='text-secondary text-center text-sm'>加载中...</div>
			</div>
		)
	}

	if (isLoading) {
		return (
			<div className='flex min-h-[70vh] items-center justify-center'>
				<div className='text-secondary text-center text-sm'>加载中...</div>
			</div>
		)
	}

	return (
		<>


			<GridView shares={shares} isEditMode={isEditMode} onUpdate={handleUpdate} onDelete={handleDelete} />

			<motion.div initial={{ opacity: 0, scale: 0.6 }} animate={{ opacity: 1, scale: 1 }} className='absolute top-4 right-6 flex gap-3 max-sm:hidden'>
				{isEditMode ? (
					<>
						<motion.button
							whileHover={{ scale: 1.05 }}
							whileTap={{ scale: 0.95 }}
							onClick={handleCancel}
							disabled={isSaving}
							className='rounded-xl border bg-white/60 px-6 py-2 text-sm'>
							取消
						</motion.button>
						<motion.button
							whileHover={{ scale: 1.05 }}
							whileTap={{ scale: 0.95 }}
							onClick={handleAdd}
							className='rounded-xl border bg-white/60 px-6 py-2 text-sm'>
							添加
						</motion.button>
						<motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={handleSaveClick} disabled={isSaving} className='brand-btn px-6'>
							{isSaving ? '保存中...' : buttonText}
						</motion.button>
					</>
				) : (
					isAdmin && !hideEditButton && (
						<motion.button
							whileHover={{ scale: 1.05 }}
							whileTap={{ scale: 0.95 }}
							onClick={() => setIsEditMode(true)}
							className='bg-card rounded-xl border px-6 py-2 text-sm backdrop-blur-sm transition-colors hover:bg-white/80'>
							编辑
						</motion.button>
					)
				)}
			</motion.div>

			{isCreateDialogOpen && <CreateDialog share={editingShare} onClose={() => setIsCreateDialogOpen(false)} onSave={handleSaveShare} />}
		</>
	)
}
