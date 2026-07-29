'use client'

import Link from 'next/link'
import { Suspense, useState, useMemo, useRef, useEffect } from 'react'
import { motion } from 'motion/react'
import { MoreHorizontal, GripVertical, ExternalLink, Pencil, Trash2, Copy, ChevronRight, X } from 'lucide-react'
import { useNoteIndex } from '@/hooks/use-note-index'
import { cn } from '@/lib/utils'
import dayjs from 'dayjs'
import { KnowledgeSidebar } from './components/knowledge-sidebar'
import { SuggestionCard } from './components/suggestion-card'
import { WeeklySummaryCard } from './components/weekly-summary-card'
import { MoveToFolderDialog } from '@/components/move-to-folder-dialog'
import { ContextMenu, type ContextMenuItem } from '@/components/context-menu'
import { EmptyState } from '@/components/empty-state'
import { moveNoteToFolder, listFolders, findFolderPath, type FolderNode } from '@/lib/api/folders'
import { deleteNote } from '@/lib/api/notes'
import { useRouter, useSearchParams } from 'next/navigation'
import { getContentEditHref, getContentDetailHref, type ContentType } from '@/lib/content-routes'
import { toast } from 'sonner'
import { useAdminAuth } from '@/hooks/use-admin-auth'

const typeLabels = { note: '笔记', blog: '博客', mistake: '错题' }
const typeColors = { note: 'bg-blue-500/20 text-blue-600', blog: 'bg-green-500/20 text-green-600', mistake: 'bg-red-500/20 text-red-600' }
const diffColors = { easy: 'bg-emerald-500/20 text-emerald-600', medium: 'bg-yellow-500/20 text-yellow-600', hard: 'bg-red-500/20 text-red-600' }

export default function NotesPage() {
	return (
		<Suspense fallback={<div className='py-20 text-center text-gray-400'>加载中...</div>}>
			<NotesPageContent />
		</Suspense>
	)
}

function NotesPageContent() {
	const router = useRouter()
	const searchParams = useSearchParams()
	const { isAdmin } = useAdminAuth()
	const [type, setType] = useState<string>('')
	const [q, setQ] = useState('')
	const [page, setPage] = useState(1)
	const [activeFilter, setActiveFilter] = useState('all')
	const [activeFolderId, setActiveFolderId] = useState<string | null>(searchParams.get('folder_id'))
	const [activeTag, setActiveTag] = useState<string | null>(null)
	const [moveTarget, setMoveTarget] = useState<{ slug: string; title: string } | null>(null)
	const [draggingSlug, setDraggingSlug] = useState<string | null>(null)
	const [dragOverFolderId, setDragOverFolderId] = useState<string | null>(null)
	const [folderRefreshKey, setFolderRefreshKey] = useState(0)
	const [ctxMenu, setCtxMenu] = useState<{ slug: string; title: string; type: ContentType; x: number; y: number } | null>(null)
	const [folderTree, setFolderTree] = useState<FolderNode[]>([])

	const folderPath = useMemo(() => {
		if (!activeFolderId || folderTree.length === 0) return null
		return findFolderPath(folderTree, activeFolderId)
	}, [activeFolderId, folderTree])

	useEffect(() => {
		listFolders().then(setFolderTree).catch(() => {})
	}, [folderRefreshKey])

	useEffect(() => {
		const urlFolderId = searchParams.get('folder_id')
		if (urlFolderId !== activeFolderId) {
			setActiveFolderId(urlFolderId)
		}
	}, [searchParams])

	const handleFolderChange = (folderId: string | null) => {
		setActiveFolderId(folderId)
		const params = new URLSearchParams(window.location.search)
		if (folderId) params.set('folder_id', folderId)
		else params.delete('folder_id')
		const qs = params.toString()
		router.replace(`/notes${qs ? `?${qs}` : ''}`, { scroll: false })
	}

	const handleTagChange = (tag: string | null) => {
		setActiveTag(tag)
		setPage(1)
	}

	const handleDropToFolder = async (folderId: string | null) => {
		if (!draggingSlug) return
		try {
			await moveNoteToFolder(draggingSlug, folderId)
			toast.success(folderId ? '已移动到文件夹' : '已移回收件箱')
			mutate()
			setFolderRefreshKey(key => key + 1)
		} catch (e: any) {
			toast.error('移动失败: ' + e.message)
		} finally {
			setDraggingSlug(null)
			setDragOverFolderId(null)
		}
	}

	const handleFilterChange = (filter: string) => {
		setActiveFilter(filter)
		setPage(1)
		if (filter === 'all') setType('')
		else if (filter === 'inbox') setType('')
		else if (['note', 'blog', 'mistake'].includes(filter)) setType(filter)
	}

	const showDashboard = activeFilter === 'all' && !activeFolderId && !activeTag && !q

	const { data, isLoading, mutate } = useNoteIndex({
		type: (type as any) || undefined,
		status: 'published',
		q: q || undefined,
		tag: activeTag || undefined,
		folder_id: activeFolderId || undefined,
		inbox: activeFilter === 'inbox' ? true : undefined,
		page,
		size: 20
	})

	const tagsRef = useRef(new Map<number, { id: number; name: string }>())

	const pageTags = useMemo(() => {
		if (!data?.items) return Array.from(tagsRef.current.values())
		for (const item of data.items) {
			for (const tag of item.tags) {
				if (!tagsRef.current.has(tag.id)) tagsRef.current.set(tag.id, tag)
			}
		}
		return Array.from(tagsRef.current.values())
	}, [data?.items])

	const getContextMenuItems = (): ContextMenuItem[] => {
		if (!ctxMenu) return []
		const folderQuery = activeFolderId ? `?folder_id=${encodeURIComponent(activeFolderId)}` : ''
		const items: ContextMenuItem[] = [
			{ label: '打开', icon: <ExternalLink size={14} />, onClick: () => router.push(getContentDetailHref(ctxMenu.type, ctxMenu.slug) + folderQuery) },
			{
				label: '复制链接',
				icon: <Copy size={14} />,
				onClick: () => {
					navigator.clipboard.writeText(`${window.location.origin}${getContentDetailHref(ctxMenu.type, ctxMenu.slug)}${folderQuery}`)
					toast.success('链接已复制')
				}
			}
		]
		if (isAdmin) {
			items.push(
				{ label: '编辑', icon: <Pencil size={14} />, onClick: () => router.push(getContentEditHref(ctxMenu.type, ctxMenu.slug) + (activeFolderId ? `?folder_id=${encodeURIComponent(activeFolderId)}` : '')) },
				{ label: '移动到文件夹', icon: <GripVertical size={14} />, onClick: () => setMoveTarget({ slug: ctxMenu.slug, title: ctxMenu.title }) },
				{
					label: '删除',
					icon: <Trash2 size={14} />,
					variant: 'danger',
					onClick: async () => {
						if (!confirm(`确定要删除「${ctxMenu.title}」吗？`)) return
						try {
							await deleteNote(ctxMenu.slug)
							toast.success('已删除')
							mutate()
						} catch (e: any) {
							toast.error('删除失败: ' + e.message)
						}
					}
				}
			)
		}
		return items
	}

	const getCreateAction = () => {
		// Route Cutover: 旧 write-* 入口已停用，统一指向 /manage/* 主线
		if (activeFilter === 'mistake') return { label: '采集错题', href: '/manage/capture' }
		return { label: '工作区', href: '/manage/dashboard' }
	}

	const emptyDescription = isAdmin ? '可以从工作区创建和整理内容' : '暂时没有公开笔记'

	return (
		<div className='mx-auto max-w-6xl px-4 py-8'>
			<motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className='mb-6 text-2xl font-bold'>
				笔记
			</motion.h1>

			<div className='flex gap-6'>
				<KnowledgeSidebar
					activeFilter={activeFilter}
					activeFolderId={activeFolderId}
					activeTag={activeTag}
					onFilterChange={handleFilterChange}
					onFolderChange={handleFolderChange}
					onTagChange={handleTagChange}
					canManage={isAdmin}
					onDropNote={isAdmin ? handleDropToFolder : undefined}
					dragOverFolderId={isAdmin ? dragOverFolderId : null}
					onDragOverFolderChange={isAdmin ? setDragOverFolderId : undefined}
					contentTypes={['note', 'blog']}
					tags={pageTags}
					refreshKey={folderRefreshKey}
				/>

				<div className='min-w-0 flex-1'>
					<div className='mb-6 flex flex-wrap items-center gap-3'>
						<input
							value={q}
							onChange={e => {
								setQ(e.target.value)
								setPage(1)
							}}
							placeholder='搜索...'
							className='rounded-xl border border-white/40 bg-white/60 px-4 py-2 backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
						/>
						<div className='flex gap-2'>
							{['', 'note', 'blog', 'mistake'].map(t => (
								<button
									key={t}
									onClick={() => {
										setType(t)
										setPage(1)
										setActiveFilter(t || 'all')
										handleFolderChange(null)
										setActiveTag(null)
									}}
									className={cn(
										'rounded-full px-3 py-1 text-sm transition-colors',
										type === t ? 'bg-[var(--color-brand)] text-white' : 'bg-white/60 hover:bg-white/80'
									)}>
									{t ? typeLabels[t as keyof typeof typeLabels] : '全部'}
								</button>
							))}
						</div>
						{isAdmin &&
							(() => {
								const createAction = getCreateAction()
								return (
									<Link
										href={createAction.href}
										className='ml-auto rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white transition-transform hover:scale-105 active:scale-95'>
										{createAction.label}
									</Link>
								)
							})()}
					</div>

					{isAdmin && <SuggestionCard onExecuted={() => mutate()} defaultExpanded={showDashboard} />}
					{isAdmin && showDashboard && <WeeklySummaryCard />}

					{folderPath && (
						<div className='mb-4 flex items-center gap-1 text-sm text-gray-500'>
							<button
								type='button'
								onClick={() => handleFolderChange(null)}
								className='rounded px-1 transition-colors hover:bg-white/60 hover:text-gray-700'>
								全部
							</button>
							{folderPath.map((node, i) => (
								<span key={node.id} className='flex items-center gap-1'>
									<ChevronRight size={12} className='text-gray-300' />
									{i < folderPath.length - 1 ? (
										<button
											type='button'
											onClick={() => handleFolderChange(node.id)}
											className='rounded px-1 transition-colors hover:bg-white/60 hover:text-gray-700'>
											{node.name}
										</button>
									) : (
										<span className='font-medium text-gray-700'>{node.name}</span>
									)}
								</span>
							))}
							<button
								type='button'
								onClick={() => handleFolderChange(null)}
								aria-label='清除文件夹筛选'
								className='ml-1 rounded p-0.5 text-gray-400 transition-colors hover:bg-white/60 hover:text-gray-600'>
								<X size={12} />
							</button>
						</div>
					)}

					{isLoading ? (
						<div className='py-20 text-center text-gray-400'>加载中...</div>
					) : data?.items.length === 0 ? (
						<div className='py-20'>
							<EmptyState
								variant={activeFilter && activeFilter !== 'all' ? 'no-results' : 'no-content'}
								title={activeFilter && activeFilter !== 'all' ? '没有匹配结果' : '还没有笔记'}
								description={activeFilter && activeFilter !== 'all' ? '试试调整筛选条件' : emptyDescription}
								action={isAdmin ? getCreateAction() : null}
							/>
						</div>
					) : (
						<div className='space-y-3'>
							{data?.items.map(item => (
								<div
									key={item.id}
									draggable={isAdmin}
									onDragStart={isAdmin ? () => setDraggingSlug(item.slug) : undefined}
									onDragEnd={
										isAdmin
											? () => {
													setDraggingSlug(null)
													setDragOverFolderId(null)
												}
											: undefined
									}
									onContextMenu={e => {
										e.preventDefault()
										setCtxMenu({ slug: item.slug, title: item.title, type: item.type, x: e.clientX, y: e.clientY })
									}}
									className={cn(draggingSlug === item.slug && 'opacity-50')}>
									<Link
										href={getContentDetailHref(item.type, item.slug) + (activeFolderId ? `?folder_id=${encodeURIComponent(activeFolderId)}` : '')}
										className='block rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm transition-all hover:bg-white/80 hover:shadow-sm'>
										<div className='mb-2 flex items-center gap-2'>
											<span className={cn('rounded-full px-2 py-0.5 text-xs', typeColors[item.type])}>{typeLabels[item.type]}</span>
											{item.difficulty && <span className={cn('rounded-full px-2 py-0.5 text-xs', diffColors[item.difficulty])}>{item.difficulty}</span>}
											{item.subject && (
												<span className='max-w-[120px] truncate rounded-full bg-purple-500/20 px-2 py-0.5 text-xs text-purple-600'>{item.subject}</span>
											)}
											{isAdmin && (
												<button
													type='button'
													onClick={e => {
														e.preventDefault()
														e.stopPropagation()
														setMoveTarget({ slug: item.slug, title: item.title })
													}}
													className='ml-auto shrink-0 rounded-md p-1 text-gray-400 transition-colors hover:bg-white/60 hover:text-gray-600'
													aria-label='移动到文件夹'>
													<MoreHorizontal size={14} />
												</button>
											)}
											<span className='shrink-0 text-xs text-gray-400'>{dayjs(item.updated_at).format('YYYY-MM-DD')}</span>
										</div>
										<h3 className='truncate font-medium'>{item.title}</h3>
										{item.summary && <p className='mt-1 line-clamp-2 text-sm text-gray-500'>{item.summary}</p>}
										{item.tags.length > 0 && (
											<div className='mt-2 flex flex-wrap gap-1'>
												{item.tags.map(tag => (
													<span key={tag.id} className='rounded bg-gray-200/60 px-1.5 py-0.5 text-xs text-gray-500'>
														{tag.name}
													</span>
												))}
											</div>
										)}
										{item.type === 'mistake' && item.next_review && (
											<div className='mt-2 text-xs text-orange-500'>下次复习: {dayjs(item.next_review).format('YYYY-MM-DD')}</div>
										)}
									</Link>
								</div>
							))}
						</div>
					)}

					{data && data.total > 20 && (
						<div className='mt-6 flex justify-center gap-2'>
							<button disabled={page <= 1} onClick={() => setPage(p => p - 1)} className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'>
								上一页
							</button>
							<span className='px-3 py-1 text-sm text-gray-500'>
								{page} / {Math.ceil(data.total / 20)}
							</span>
							<button
								disabled={page >= Math.ceil(data.total / 20)}
								onClick={() => setPage(p => p + 1)}
								className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'>
								下一页
							</button>
						</div>
					)}
				</div>
			</div>

			{ctxMenu && <ContextMenu open={!!ctxMenu} position={{ x: ctxMenu.x, y: ctxMenu.y }} items={getContextMenuItems()} onClose={() => setCtxMenu(null)} />}

			{moveTarget && (
				<MoveToFolderDialog
					slug={moveTarget.slug}
					noteTitle={moveTarget.title}
					open={!!moveTarget}
					onClose={() => setMoveTarget(null)}
					onMoved={() => {
						mutate()
						setFolderRefreshKey(key => key + 1)
						setMoveTarget(null)
					}}
				/>
			)}
		</div>
	)
}
