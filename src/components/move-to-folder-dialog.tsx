'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { FolderOpen, Folder, X, Check, ChevronRight, ChevronDown } from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { listFolders, moveNoteToFolder, type FolderNode } from '@/lib/api/folders'

type MoveToFolderDialogProps = {
	slug: string
	noteTitle: string
	open: boolean
	onClose: () => void
	onMoved?: () => void
}

export function MoveToFolderDialog({ slug, noteTitle, open, onClose, onMoved }: MoveToFolderDialogProps) {
	const [folders, setFolders] = useState<FolderNode[]>([])
	const [loading, setLoading] = useState(false)
	const [moving, setMoving] = useState(false)
	const [expanded, setExpanded] = useState<Set<string>>(new Set())

	useEffect(() => {
		if (open) {
			setLoading(true)
			listFolders().then(f => { setFolders(f); setLoading(false) }).catch(() => setLoading(false))
		}
	}, [open])

	const toggleExpand = (id: string) => {
		setExpanded(prev => {
			const next = new Set(prev)
			next.has(id) ? next.delete(id) : next.add(id)
			return next
		})
	}

	const handleMove = async (folderId: string | null) => {
		setMoving(true)
		try {
			await moveNoteToFolder(slug, folderId)
			toast.success(folderId ? '已移动到文件夹' : '已移回收件箱')
			onMoved?.()
			onClose()
		} catch (e: any) {
			toast.error('移动失败: ' + e.message)
		} finally {
			setMoving(false)
		}
	}

	const renderTree = (nodes: FolderNode[], depth = 0) => {
		return nodes.map(node => (
			<div key={node.id}>
				<button
					onClick={() => handleMove(node.id)}
					disabled={moving}
					className='flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-white/80 disabled:opacity-50'
					style={{ paddingLeft: `${12 + depth * 16}px` }}
				>
					{node.children.length > 0 ? (
						<button
							type='button'
							onClick={e => { e.stopPropagation(); toggleExpand(node.id) }}
							className='shrink-0 text-gray-400'
						>
							{expanded.has(node.id) ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
						</button>
					) : (
						<span className='w-3.5 shrink-0' />
					)}
					{expanded.has(node.id) ? <FolderOpen size={15} className='shrink-0 text-amber-500' /> : <Folder size={15} className='shrink-0 text-amber-500' />}
					<span className='truncate'>{node.name}</span>
				</button>
				{expanded.has(node.id) && node.children.length > 0 && renderTree(node.children, depth + 1)}
			</div>
		))
	}

	return (
		<AnimatePresence>
			{open && (
				<>
					<motion.div
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						exit={{ opacity: 0 }}
						className='fixed inset-0 z-50 bg-black/30'
						onClick={onClose}
					/>
					<motion.div
						initial={{ opacity: 0, y: 50 }}
						animate={{ opacity: 1, y: 0 }}
						exit={{ opacity: 0, y: 50 }}
						className='fixed inset-x-4 bottom-4 top-auto z-50 mx-auto max-w-md rounded-2xl border border-white/40 bg-white/95 p-4 shadow-xl backdrop-blur-xl'
					>
						<div className='mb-3 flex items-center justify-between'>
							<div>
								<h3 className='text-sm font-semibold'>移动到文件夹</h3>
								<p className='mt-0.5 max-w-[250px] truncate text-xs text-gray-500'>{noteTitle}</p>
							</div>
							<button onClick={onClose} className='text-gray-400 hover:text-gray-600' aria-label='关闭'>
								<X size={18} />
							</button>
						</div>

						<div className='max-h-60 overflow-y-auto'>
							{loading ? (
								<div className='py-8 text-center text-sm text-gray-400'>加载中...</div>
							) : (
								<>
									<button
										onClick={() => handleMove(null)}
										disabled={moving}
										className='flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-gray-600 transition-colors hover:bg-white/80 disabled:opacity-50'
									>
										<span className='w-3.5' />
										<span>收件箱（取消归档）</span>
									</button>
									{folders.length > 0 ? (
										renderTree(folders)
									) : (
										<div className='py-4 text-center text-sm text-gray-400'>暂无文件夹</div>
									)}
								</>
							)}
						</div>
					</motion.div>
				</>
			)}
		</AnimatePresence>
	)
}
