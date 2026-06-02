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
	Tag,
	Menu,
	X,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { listFolders, type FolderNode } from '@/lib/api/folders'
import { listTags, type Tag as TagType } from '@/lib/api/meta'

type SidebarItem = {
	id: string
	label: string
	icon: React.ReactNode
	href?: string
	type?: string
	count?: number
}

type KnowledgeSidebarProps = {
	activeFilter: string
	activeFolderId: string | null
	activeTag: string | null
	onFilterChange: (filter: string) => void
	onFolderChange: (folderId: string | null) => void
	onTagChange: (tag: string | null) => void
}

export function KnowledgeSidebar({
	activeFilter, activeFolderId, activeTag,
	onFilterChange, onFolderChange, onTagChange,
}: KnowledgeSidebarProps) {
	const [folders, setFolders] = useState<FolderNode[]>([])
	const [tags, setTags] = useState<TagType[]>([])
	const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())
	const [mobileOpen, setMobileOpen] = useState(false)

	useEffect(() => {
		listFolders().then(setFolders).catch(() => {})
		listTags().then(setTags).catch(() => {})
	}, [])

	const toggleFolder = (id: string) => {
		setExpandedFolders(prev => {
			const next = new Set(prev)
			next.has(id) ? next.delete(id) : next.add(id)
			return next
		})
	}

	const navItems: SidebarItem[] = [
		{ id: 'all', label: '全部内容', icon: <FileText size={16} /> },
		{ id: 'inbox', label: '收件箱', icon: <Inbox size={16} /> },
		{ id: 'note', label: '笔记', icon: <FileText size={16} />, type: 'note' },
		{ id: 'blog', label: '博客', icon: <Newspaper size={16} />, type: 'blog' },
		{ id: 'mistake', label: '错题', icon: <AlertCircle size={16} />, type: 'mistake' },
	]

	const renderFolderTree = (nodes: FolderNode[], depth = 0) => {
		return nodes.map(node => (
			<div key={node.id}>
				<button
					onClick={() => { onFolderChange(node.id); onFilterChange('') }}
					className={cn(
						'flex w-full items-center gap-2 rounded-lg px-3 py-1.5 text-sm transition-colors hover:bg-white/60',
						activeFolderId === node.id ? 'bg-[var(--color-brand)]/10 text-[var(--color-brand)] font-medium' : 'text-gray-600'
					)}
					style={{ paddingLeft: `${12 + depth * 16}px` }}
				>
					{node.children.length > 0 ? (
						<button
							type='button'
							onClick={(e) => { e.stopPropagation(); toggleFolder(node.id) }}
							className='shrink-0 text-gray-400'
						>
							{expandedFolders.has(node.id) ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
						</button>
					) : (
						<span className='w-3.5 shrink-0' />
					)}
					{expandedFolders.has(node.id) ? <FolderOpen size={15} className='shrink-0 text-amber-500' /> : <Folder size={15} className='shrink-0 text-amber-500' />}
					<span className='truncate'>{node.name}</span>
					{node.note_count > 0 && <span className='ml-auto text-xs text-gray-400'>{node.note_count}</span>}
				</button>
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

			{tags.length > 0 && (
				<>
					<div className='mx-3 border-t border-white/20' />
					<div className='p-3'>
						<div className='mb-2 px-3 text-xs font-medium text-gray-400'>标签</div>
						<div className='flex flex-wrap gap-1.5 px-3'>
							{tags.map(tag => (
								<button
									key={tag.id}
									onClick={() => { onTagChange(tag.name); onFilterChange(''); onFolderChange(null) }}
									className={cn(
										'rounded-full px-2.5 py-1 text-xs transition-colors',
										activeTag === tag.name ? 'bg-[var(--color-brand)] text-white' : 'bg-white/60 text-gray-600 hover:bg-white/80'
									)}
								>
									{tag.name}
								</button>
							))}
						</div>
					</div>
				</>
			)}
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
									<span className='text-sm font-medium'>知识库</span>
									<button onClick={() => setMobileOpen(false)} className='text-gray-400 hover:text-gray-600'>
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
