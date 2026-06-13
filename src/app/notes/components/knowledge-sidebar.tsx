'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'motion/react'
import { FolderOpen, Folder, Inbox, FileText, Newspaper, AlertCircle, ChevronRight, ChevronDown, ChevronUp, Tag, Menu, X, Plus, Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { listFolders, reorderFolders, createFolder, deleteFolder, renameFolder, type FolderNode } from '@/lib/api/folders'
import { listTags, renameTag, deleteTag, type Tag as TagType } from '@/lib/api/meta'
import { ContextMenu, type ContextMenuItem } from '@/components/context-menu'
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
	canManage?: boolean
}

export function KnowledgeSidebar({
	mode = 'knowledge',
	activeFilter,
	activeFolderId,
	activeTag,
	onFilterChange,
	onFolderChange,
	onTagChange,
	onDropNote,
	dragOverFolderId,
	onDragOverFolderChange,
	contentTypes,
	tags: externalTags,
	canManage = false
}: KnowledgeSidebarProps) {
	const [folders, setFolders] = useState<FolderNode[]>([])
	const [internalTags, setInternalTags] = useState<TagType[]>([])
	const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())
	const [mobileOpen, setMobileOpen] = useState(false)
	const [tagsCollapsed, setTagsCollapsed] = useState(false)
	const [tagsExpanded, setTagsExpanded] = useState(false)
	const [creatingFolder, setCreatingFolder] = useState(false)
	const [newFolderName, setNewFolderName] = useState('')
	const [ctxMenu, setCtxMenu] = useState<{ type: 'folder' | 'tag'; id: string; name: string; x: number; y: number } | null>(null)

	const tags = externalTags ?? internalTags

	useEffect(() => {
		listFolders()
			.then(setFolders)
			.catch(() => {})
		if (!externalTags) {
			listTags()
				.then(setInternalTags)
				.catch(() => {})
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
		if (!canManage) return
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

	const handleCreateFolder = async () => {
		if (!canManage) return
		const name = newFolderName.trim()
		if (!name) {
			toast.warning('请输入文件夹名')
			return
		}
		try {
			await createFolder({ name })
			const updated = await listFolders()
			setFolders(updated)
			setNewFolderName('')
			setCreatingFolder(false)
			toast.success('文件夹已创建')
		} catch (e: any) {
			toast.error('创建失败: ' + e.message)
		}
	}

	const getContextMenuItems = (): ContextMenuItem[] => {
		if (!ctxMenu) return []
		if (ctxMenu.type === 'folder') {
			const items: ContextMenuItem[] = [
				{
					label: '筛选',
					icon: <Folder size={14} />,
					onClick: () => {
						onFolderChange(ctxMenu.id)
						onFilterChange('')
						onTagChange(null)
					}
				},
				{
					label: '复制名称',
					icon: <FileText size={14} />,
					onClick: () => {
						navigator.clipboard.writeText(ctxMenu.name)
						toast.success('已复制')
					}
				}
			]
			if (canManage) {
				items.push(
					{
						label: '新建子文件夹',
						icon: <Plus size={14} />,
						onClick: async () => {
							const name = prompt('子文件夹名称:')
							if (!name) return
							try {
								await createFolder({ name, parent_id: ctxMenu.id })
								setFolders(await listFolders())
								toast.success('子文件夹已创建')
							} catch (e: any) {
								toast.error('创建失败: ' + e.message)
							}
						}
					},
					{
						label: '重命名',
						icon: <Tag size={14} />,
						onClick: async () => {
							const name = prompt('新名称:', ctxMenu.name)
							if (!name || name === ctxMenu.name) return
							try {
								await renameFolder(ctxMenu.id, name)
								setFolders(await listFolders())
								toast.success('已重命名')
							} catch (e: any) {
								toast.error('重命名失败: ' + e.message)
							}
						}
					},
					{
						label: '删除',
						icon: <AlertCircle size={14} />,
						variant: 'danger',
						onClick: async () => {
							if (!confirm(`确定删除文件夹「${ctxMenu.name}」？内容将移回收件箱。`)) return
							try {
								await deleteFolder(ctxMenu.id)
								setFolders(await listFolders())
								if (activeFolderId === ctxMenu.id) onFolderChange(null)
								toast.success('已删除')
							} catch (e: any) {
								toast.error('删除失败: ' + e.message)
							}
						}
					}
				)
			}
			return items
		}
		if (ctxMenu.type === 'tag') {
			const items: ContextMenuItem[] = [
				{
					label: '筛选',
					icon: <FileText size={14} />,
					onClick: () => {
						onTagChange(ctxMenu.name)
						onFilterChange('')
						onFolderChange(null)
					}
				},
				{
					label: '复制名称',
					icon: <FileText size={14} />,
					onClick: () => {
						navigator.clipboard.writeText(ctxMenu.name)
						toast.success('已复制')
					}
				}
			]
			if (canManage) {
				items.push(
					{
						label: '重命名',
						icon: <Tag size={14} />,
						onClick: async () => {
							const name = prompt('新名称:', ctxMenu.name)
							if (!name || name === ctxMenu.name) return
							try {
								const tag = tags.find(t => t.name === ctxMenu.name)
								if (tag) {
									await renameTag(tag.id, name)
									if (!externalTags) setInternalTags(await listTags())
									if (activeTag === ctxMenu.name) onTagChange(name)
									toast.success('已重命名')
								}
							} catch (e: any) {
								toast.error('重命名失败: ' + e.message)
							}
						}
					},
					{
						label: '删除',
						icon: <AlertCircle size={14} />,
						variant: 'danger',
						onClick: async () => {
							if (!confirm(`确定删除标签「${ctxMenu.name}」？不会删除关联内容。`)) return
							try {
								const tag = tags.find(t => t.name === ctxMenu.name)
								if (tag) {
									await deleteTag(tag.id)
									if (!externalTags) setInternalTags(await listTags())
									if (activeTag === ctxMenu.name) onTagChange(null)
									toast.success('已删除')
								}
							} catch (e: any) {
								toast.error('删除失败: ' + e.message)
							}
						}
					}
				)
			}
			return items
		}
		return []
	}

	const navItems: SidebarItem[] =
		mode === 'mistake'
			? [{ id: 'all', label: '全部错题', icon: <AlertCircle size={16} /> }]
			: [
					{ id: 'all', label: '全部内容', icon: <FileText size={16} /> },
					{ id: 'inbox', label: '收件箱', icon: <Inbox size={16} /> },
					{ id: 'note', label: '笔记', icon: <FileText size={16} />, type: 'note' },
					{ id: 'blog', label: '博客', icon: <Newspaper size={16} />, type: 'blog' },
					{ id: 'mistake', label: '错题', icon: <AlertCircle size={16} />, type: 'mistake' }
				].filter(item => {
					if (!contentTypes || !item.type) return true
					return contentTypes.includes(item.type as 'note' | 'blog' | 'mistake')
				})

	const renderFolderTree = (nodes: FolderNode[], depth = 0) => {
		return nodes.map(node => (
			<div key={node.id}>
				<div
					onDragOver={
						canManage
							? e => {
									e.preventDefault()
									e.stopPropagation()
									onDragOverFolderChange?.(node.id)
								}
							: undefined
					}
					onDragLeave={
						canManage
							? e => {
									e.stopPropagation()
									onDragOverFolderChange?.(null)
								}
							: undefined
					}
					onDrop={
						canManage
							? e => {
									e.preventDefault()
									e.stopPropagation()
									onDropNote?.(node.id)
									onDragOverFolderChange?.(null)
								}
							: undefined
					}
					onContextMenu={e => {
						e.preventDefault()
						setCtxMenu({ type: 'folder', id: node.id, name: node.name, x: e.clientX, y: e.clientY })
					}}
					className={cn(
						'group flex w-full items-center gap-1 rounded-lg py-1.5 text-sm transition-colors hover:bg-white/60',
						activeFolderId === node.id ? 'bg-[var(--color-brand)]/10 font-medium text-[var(--color-brand)]' : 'text-gray-600',
						dragOverFolderId === node.id && 'bg-[var(--color-brand)]/5 ring-2 ring-[var(--color-brand)]/40'
					)}
					style={{ paddingLeft: `${12 + depth * 16}px`, paddingRight: '8px' }}>
					{node.children.length > 0 ? (
						<button
							type='button'
							onClick={() => toggleFolder(node.id)}
							className='shrink-0 rounded p-0.5 text-gray-400 hover:text-gray-600'
							aria-label={expandedFolders.has(node.id) ? '折叠' : '展开'}>
							{expandedFolders.has(node.id) ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
						</button>
					) : (
						<span className='w-5 shrink-0' />
					)}
					<button
						type='button'
						onClick={() => {
							onFolderChange(node.id)
							onFilterChange('')
						}}
						className='flex min-w-0 flex-1 items-center gap-2'>
						{expandedFolders.has(node.id) ? (
							<FolderOpen size={15} className='shrink-0 text-amber-500' />
						) : (
							<Folder size={15} className='shrink-0 text-amber-500' />
						)}
						<span className='truncate'>{node.name}</span>
					</button>
					{node.note_count > 0 && <span className='shrink-0 text-xs text-gray-400'>{node.note_count}</span>}
					{canManage && (
						<span className='flex shrink-0 gap-0.5 opacity-0 transition-opacity group-hover:opacity-100'>
							<button
								type='button'
								onClick={() => handleReorder(node.id, 'up')}
								className='rounded p-0.5 text-gray-400 hover:bg-white/60 hover:text-gray-600'
								aria-label='上移'>
								<ChevronUp size={12} />
							</button>
							<button
								type='button'
								onClick={() => handleReorder(node.id, 'down')}
								className='rounded p-0.5 text-gray-400 hover:bg-white/60 hover:text-gray-600'
								aria-label='下移'>
								<ChevronDown size={12} />
							</button>
						</span>
					)}
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
						onClick={() => {
							onFilterChange(item.id)
							onFolderChange(null)
							onTagChange(null)
						}}
						className={cn(
							'flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-white/60',
							activeFilter === item.id && !activeFolderId ? 'bg-[var(--color-brand)]/10 font-medium text-[var(--color-brand)]' : 'text-gray-600'
						)}>
						{item.icon}
						<span>{item.label}</span>
					</button>
				))}
			</nav>

			<>
				<div className='mx-3 border-t border-white/20' />
				<div className='p-3'>
					<div className='mb-2 flex items-center justify-between px-3'>
						<span className='text-xs font-medium text-gray-400'>文件夹</span>
						{canManage &&
							(creatingFolder ? (
								<div className='flex items-center gap-1'>
									<input
										value={newFolderName}
										onChange={e => setNewFolderName(e.target.value)}
										onKeyDown={e => {
											if (e.key === 'Enter') handleCreateFolder()
											if (e.key === 'Escape') {
												setCreatingFolder(false)
												setNewFolderName('')
											}
										}}
										placeholder='文件夹名'
										autoFocus
										className='w-20 rounded border border-white/40 bg-white/60 px-1.5 py-0.5 text-[10px] outline-none'
									/>
									<button type='button' onClick={handleCreateFolder} aria-label='确认创建' className='rounded p-0.5 text-green-500 hover:bg-white/60'>
										<Check size={12} />
									</button>
									<button
										type='button'
										onClick={() => {
											setCreatingFolder(false)
											setNewFolderName('')
										}}
										aria-label='取消创建'
										className='rounded p-0.5 text-gray-400 hover:bg-white/60'>
										<X size={12} />
									</button>
								</div>
							) : (
								<button
									type='button'
									onClick={() => setCreatingFolder(true)}
									aria-label='创建文件夹'
									className='rounded p-0.5 text-gray-400 hover:bg-white/60 hover:text-gray-600'>
									<Plus size={14} />
								</button>
							))}
					</div>
					{folders.length > 0 && renderFolderTree(folders)}
				</div>
			</>

			<div className='mx-3 border-t border-white/20' />
			<div className='p-3'>
				<button
					type='button'
					onClick={() => setTagsCollapsed(!tagsCollapsed)}
					className='mb-2 flex w-full items-center gap-1 px-3 text-xs font-medium text-gray-400 hover:text-gray-600'
					aria-label={tagsCollapsed ? '展开标签' : '折叠标签'}>
					{tagsCollapsed ? <ChevronRight size={12} /> : <ChevronDown size={12} />}
					标签
				</button>
				{!tagsCollapsed &&
					(tags.length > 0 ? (
						<div className='flex flex-wrap gap-1.5 px-3'>
							{(tagsExpanded ? tags : tags.slice(0, 12)).map(tag => (
								<button
									key={tag.id}
									onClick={() => {
										if (activeTag === tag.name) {
											onTagChange(null)
											onFilterChange('all')
											return
										}
										onTagChange(tag.name)
										onFilterChange('')
										onFolderChange(null)
									}}
									onContextMenu={e => {
										e.preventDefault()
										setCtxMenu({ type: 'tag', id: String(tag.id), name: tag.name, x: e.clientX, y: e.clientY })
									}}
									className={cn(
										'rounded-full px-2.5 py-1 text-xs font-medium transition-colors',
										activeTag === tag.name ? 'bg-[var(--color-brand)] text-white shadow-sm' : 'bg-white/60 text-gray-600 hover:bg-white/80 hover:text-gray-800'
									)}>
									{tag.name}
								</button>
							))}
							{tags.length > 12 && (
								<button
									type='button'
									onClick={() => setTagsExpanded(!tagsExpanded)}
									className='rounded-full px-2.5 py-1 text-xs text-gray-400 hover:text-gray-600 hover:bg-white/60'
								>
									{tagsExpanded ? '收起' : `更多 (${tags.length - 12})`}
								</button>
							)}
						</div>
					) : (
						<p className='px-3 text-xs text-gray-400'>暂无标签</p>
					))}
			</div>
		</div>
	)

	return (
		<>
			<div className='hidden lg:block'>
				<div className='sticky top-24 w-56 shrink-0 rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm'>{sidebarContent}</div>
			</div>

			<div className='lg:hidden'>
				<button
					onClick={() => setMobileOpen(true)}
					className='fixed bottom-4 left-4 z-40 flex h-10 w-10 items-center justify-center rounded-full bg-[var(--color-brand)] text-white shadow-lg'
					aria-label='打开知识库导航'>
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
								className='fixed top-0 left-0 z-50 h-full w-64 overflow-y-auto border-r border-white/40 bg-white/95 backdrop-blur-xl'>
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

			{ctxMenu && <ContextMenu open={!!ctxMenu} position={{ x: ctxMenu.x, y: ctxMenu.y }} items={getContextMenuItems()} onClose={() => setCtxMenu(null)} />}
		</>
	)
}
