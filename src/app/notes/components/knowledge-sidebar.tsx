'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'motion/react'
import {
	FolderOpen,
	Folder,
	Inbox,
	FileText,
	Newspaper,
	AlertCircle,
	ChevronRight,
	ChevronDown,
	ChevronUp,
	Tag,
	Menu,
	X,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { listFolders, reorderFolders, type FolderNode } from '@/lib/api/folders'
import { listTags, type Tag as TagType } from '@/lib/api/meta'
import { toast } from 'sonner'

type SidebarItem = {
	id: string
	label: string
	icon: React.ReactNode
	href?: string
	type?: string
	count?: number
}

type KnowledgeSidebarProps = {
	mode?: 'knowledge' | 'mistake'
	activeFilter: string
	activeFolderId: string | null
	activeTag: string | null
	onFilterChange: (filter: string) => void
	onFolderChange: (folderId: string | null) => void
	onTagChange: (tag: string | null) => void
	onDropNote?: (folderId: string | null) => void
	dragOverFolderId?: string | null
	onDragOverFolderChange?: (folderId: string | null) => void
	contentTypes?: Array<'note' | 'blog' | 'mistake'>
	tags?: TagType[]
}

export function KnowledgeSidebar({
	mode = 'knowledge',
	activeFilter, activeFolderId, activeTag,
	onFilterChange, onFolderChange, onTagChange,
	onDropNote, dragOverFolderId, onDragOverFolderChange,
	contentTypes,
	tags: externalTags,
}: KnowledgeSidebarProps) {
	const [folders, setFolders] = useState<FolderNode[]>([])
	const [internalTags, setInternalTags] = useState<TagType[]>([])
	const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())
	const [mobileOpen, setMobileOpen] = useState(false)

	const tags = externalTags ?? internalTags

	useEffect(() => {
		listFolders().then(setFolders).catch(() => {})
		if (!externalTags) {
			listTags().then(setInternalTags).catch(() => {})
		}
	}, [externalTags])

	const toggleFolder = (id: string) => {
		setExpandedFolders(prev => {
			const next = new Set(prev)
			next.has(id) ? next.delete(id) : next.add(id)
			return next
		})
	}

	const handleReorder = async (folderId: string, direction: 'up' | 'down') => {
		const findParent = (nodes: FolderNode[], targetId: string): FolderNode | null => {
			for (const n of nodes) {
				if (n.id === targetId) return null
				if (n.children.some(c => c.id === targetId)) return n
				const found = findParent(n.children, targetId)
				if (found) return found
			}
			return null
		}

		const parent = findParent(folders, folderId)
		const siblings = parent ? parent.children : folders.filter(f => f.parent_id === null)
		const idx = siblings.findIndex(f => f.id === folderId)
		if (idx < 0) return
		const targetIdx = direction === 'up' ? idx - 1 : idx + 1
		if (targetIdx < 0 || targetIdx >= siblings.length) return

		const reordered = [...siblings]
		const [moved] = reordered.splice(idx, 1)
		reordered.splice(targetIdx, 0, moved)

		const items = reordered.map((f, i) => ({ id: f.id, sort_order: i }))
		try {
			await reorderFolders(items)
			const updated = await listFolders()
			setFolders(updated)
			toast.success('已调整顺序')
		} catch (e: any) {
			toast.error('排序失败: ' + e.message)
		}
	}

	const navItems: SidebarItem[] = mode === 'mistake'
		? [{ id: 'all', label: '全部错题', icon: <AlertCircle size={16} /> }]
		: [
			{ id: 'all', label: '全部内容', icon: <FileText size={16} /> },
			{ id: 'inbox', label: '收件箱', icon: <Inbox size={16} /> },
			{ id: 'note', label: '笔记', icon: <FileText size={16} />, type: 'note' },
			{ id: 'blog', label: '博客', icon: <Newspaper size={16} />, type: 'blog' },
			{ id: 'mistake', label: '错题', icon: <AlertCircle size={16} />, type: 'mistake' },
		].filter(item => {
			if (!contentTypes || !item.type) return true
			return contentTypes.includes(item.type as 'note' | 'blog' | 'mistake')
		})

	const renderFolderTree = (nodes: FolderNode[], depth = 0) => {
		return nodes.map(node => (
			<div key={node.id}>
				<div
					onDragOver={e => { e.preventDefault(); e.stopPropagation(); onDragOverFolderChange?.(node.id) }}
					onDragLeave={e => { e.stopPropagation(); onDragOverFolderChange?.(null) }}
					onDrop={e => { e.preventDefault(); e.stopPropagation(); onDropNote?.(node.id); onDragOverFolderChange?.(null) }}
					className={cn(
						'group flex w-full items-center gap-1 rounded-lg py-1.5 text-sm transition-colors hover:bg-white/60',
						activeFolderId === node.id ? 'bg-[var(--color-brand)]/10 text-[var(--color-brand)] font-medium' : 'text-gray-600',
						dragOverFolderId === node.id && 'ring-2 ring-[var(--color-brand)]/40 bg-[var(--color-brand)]/5'
					)}
					style={{ paddingLeft: `${12 + depth * 16}px`, paddingRight: '8px' }}
				>
					{node.children.length > 0 ? (
						<button
							type='button'
							onClick={() => toggleFolder(node.id)}
							className='shrink-0 rounded p-0.5 text-gray-400 hover:text-gray-600'
							aria-label={expandedFolders.has(node.id) ? '折叠' : '展开'}
						>
							{expandedFolders.has(node.id) ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
						</button>
					) : (
						<span className='w-5 shrink-0' />
					)}
					<button
						type='button'
						onClick={() => { onFolderChange(node.id); onFilterChange('') }}
						className='flex min-w-0 flex-1 items-center gap-2'
					>
						{expandedFolders.has(node.id) ? <FolderOpen size={15} className='shrink-0 text-amber-500' /> : <Folder size={15} className='shrink-0 text-amber-500' />}
						<span className='truncate'>{node.name}</span>
					</button>
					{node.note_count > 0 && <span className='shrink-0 text-xs text-gray-400'>{node.note_count}</span>}
					<span className='flex shrink-0 gap-0.5 opacity-0 transition-opacity group-hover:opacity-100'>
						<button
							type='button'
							onClick={() => handleReorder(node.id, 'up')}
							className='rounded p-0.5 text-gray-400 hover:bg-white/60 hover:text-gray-600'
							aria-label='上移'
						>
							<ChevronUp size={12} />
						</button>
						<button
							type='button'
							onClick={() => handleReorder(node.id, 'down')}
							className='rounded p-0.5 text-gray-400 hover:bg-white/60 hover:text-gray-600'
							aria-label='下移'
						>
							<ChevronDown size={12} />
						</button>
					</span>
				</div>
				{expandedFolders.has(node.id) && node.children.length > 0 && renderFolderTree(node.children, depth + 1)}
			</div>
		))
	}

	const sidebarContent = (
		<div className='flex h-full flex-col'>
			<nav className='space-y-0.5 p-3'>
				{navItems.map(item => (
					<button
						key={item.id}
						onClick={() => { onFilterChange(item.id); onFolderChange(null); onTagChange(null) }}
						className={cn(
							'flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-white/60',
							activeFilter === item.id && !activeFolderId ? 'bg-[var(--color-brand)]/10 text-[var(--color-brand)] font-medium' : 'text-gray-600'
						)}
					>
						{item.icon}
						<span>{item.label}</span>
					</button>
				))}
			</nav>

			{folders.length > 0 && (
				<>
					<div className='mx-3 border-t border-white/20' />
					<div className='p-3'>
						<div className='mb-2 px-3 text-xs font-medium text-gray-400'>文件夹</div>
						{renderFolderTree(folders)}
					</div>
				</>
			)}

			<div className='mx-3 border-t border-white/20' />
			<div className='p-3'>
				<div className='mb-2 px-3 text-xs font-medium text-gray-400'>标签</div>
				{tags.length > 0 ? (
					<div className='flex flex-wrap gap-1.5 px-3'>
						{tags.map(tag => (
							<button
								key={tag.id}
								onClick={() => { onTagChange(tag.name); onFilterChange(''); onFolderChange(null) }}
								className={cn(
									'rounded-full px-2.5 py-1 text-xs font-medium transition-colors',
									activeTag === tag.name
										? 'bg-[var(--color-brand)] text-white shadow-sm'
										: 'bg-white/60 text-gray-600 hover:bg-white/80 hover:text-gray-800'
								)}
							>
								{tag.name}
							</button>
						))}
					</div>
				) : (
					<p className='px-3 text-xs text-gray-400'>暂无标签</p>
				)}
			</div>
		</div>
	)

	return (
		<>
			<div className='hidden lg:block'>
				<div className='sticky top-24 w-56 shrink-0 rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm'>
					{sidebarContent}
				</div>
			</div>

			<div className='lg:hidden'>
				<button
					onClick={() => setMobileOpen(true)}
					className='fixed bottom-4 left-4 z-40 flex h-10 w-10 items-center justify-center rounded-full bg-[var(--color-brand)] text-white shadow-lg'
					aria-label='打开知识库导航'
				>
					<Menu size={18} />
				</button>

				<AnimatePresence>
					{mobileOpen && (
						<>
							<motion.div
								initial={{ opacity: 0 }}
								animate={{ opacity: 1 }}
								exit={{ opacity: 0 }}
								className='fixed inset-0 z-40 bg-black/30'
								onClick={() => setMobileOpen(false)}
							/>
							<motion.div
								initial={{ x: -280 }}
								animate={{ x: 0 }}
								exit={{ x: -280 }}
								transition={{ type: 'spring', damping: 25, stiffness: 300 }}
								className='fixed left-0 top-0 z-50 h-full w-64 overflow-y-auto border-r border-white/40 bg-white/95 backdrop-blur-xl'
							>
								<div className='flex items-center justify-between border-b border-white/20 p-4'>
									<span className='text-sm font-medium'>{mode === 'mistake' ? '错题库' : '知识库'}</span>
									<button onClick={() => setMobileOpen(false)} className='text-gray-400 hover:text-gray-600' aria-label='关闭导航' title='关闭导航'>
										<X size={18} />
									</button>
								</div>
								{sidebarContent}
							</motion.div>
						</>
					)}
				</AnimatePresence>
			</div>
		</>
	)
}
