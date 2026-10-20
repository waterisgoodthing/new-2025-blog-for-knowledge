'use client'

import Link from 'next/link'
import { Suspense, useState, useMemo, useRef, useEffect } from 'react'
import { MoreHorizontal, GripVertical, ExternalLink, Pencil, Trash2, Copy, ChevronRight, X } from 'lucide-react'
import { useNoteIndex } from '@/hooks/use-note-index'
import { cn } from '@/lib/utils'
import dayjs from 'dayjs'
import { KnowledgeSidebar } from './components/knowledge-sidebar'
import { SuggestionCard } from './components/suggestion-card'
import { WeeklySummaryCard } from './components/weekly-summary-card'
import { MoveToFolderDialog } from '@/components/move-to-folder-dialog'
import { Uiv2ContextMenu } from '@/components/ui-v2'

// 本地菜单项形状；渲染时映射为 Uiv2ContextAction。
type ContextMenuItem = {
	label: string
	icon?: React.ReactNode
	onClick: () => void
	variant?: 'default' | 'danger'
	disabled?: boolean
}

import { EmptyState } from '@/components/empty-state'
import { AsyncStatePanel } from '@/components/async-state-panel'
import { Uiv2Badge, Uiv2Button, Uiv2PageHeader } from '@/components/ui-v2'
import { moveNoteToFolder, listFolders, findFolderPath, type FolderNode } from '@/lib/api/folders'
import { deleteNote } from '@/lib/api/notes'
import { useRouter, useSearchParams } from 'next/navigation'
import { getContentEditHref, getContentDetailHref, type ContentType } from '@/lib/content-routes'
import { toast } from 'sonner'
import { useAdminAuth } from '@/hooks/use-admin-auth'
import { markRenderReady } from '@/lib/render-readiness'

const typeLabels = { note: '笔记', blog: '博客', mistake: '错题' }
const diffColors = { easy: 'bg-emerald-500/20 text-emerald-600', medium: 'bg-yellow-500/20 text-yellow-600', hard: 'bg-red-500/20 text-red-600' }

export default function NotesPage() {
	return (
		<Suspense fallback={<div className='py-20 text-center' style={{ color: 'var(--editorial-text-tertiary)' }}>加载中...</div>}>
			<NotesPageContent />
		</Suspense>
	)
}

function NotesPageContent() {
	const router = useRouter()
	const searchParams = useSearchParams()
	const { isAdmin } = useAdminAuth({ mode: 'optional' })
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
	const resultRegionRef = useRef<HTMLDivElement>(null)
	const retryRequestedRef = useRef(false)

	const folderPath = useMemo(() => {
		if (!activeFolderId || folderTree.length === 0) return null
		return findFolderPath(folderTree, activeFolderId)
	}, [activeFolderId, folderTree])

	useEffect(() => {
		if (!isAdmin) {
			setFolderTree([])
			return
		}
		listFolders().then(setFolderTree).catch(() => {})
	}, [isAdmin, folderRefreshKey])

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

	const { data, error, isLoading, mutate } = useNoteIndex({
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
	const renderState = isLoading ? 'loading' : error ? 'error' : data?.items.length === 0 ? 'empty' : data ? 'ready' : 'loading'

	useEffect(() => {
		if (renderState === 'ready' || renderState === 'empty') markRenderReady('notes:list-ready')
		if ((renderState === 'ready' || renderState === 'empty') && retryRequestedRef.current) {
			retryRequestedRef.current = false
			resultRegionRef.current?.focus()
		}
	}, [renderState])

	const retryNotes = () => {
		retryRequestedRef.current = true
		return mutate()
	}

	return (
		<main
			className='mx-auto max-w-6xl rounded-[16px] px-4 py-8 sm:px-6'
			data-render-state={renderState}
			data-surface='editorial'
			style={{ background: 'var(--editorial-bg)', color: 'var(--editorial-text-primary)' }}>
			<div className='mb-6'>
				<Uiv2PageHeader title='笔记' />
			</div>

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
							aria-label='搜索笔记'
							className='rounded-xl border px-4 py-2 outline-none focus:border-[var(--brand)]'
							style={{ background: 'var(--editorial-surface)', borderColor: 'var(--editorial-border)', color: 'var(--editorial-text-primary)' }}
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
									className={cn('rounded-full border px-3 py-1 text-sm transition-colors', type === t && 'font-medium')}
									style={{
										background: type === t ? 'var(--brand, #3db8a8)' : 'var(--editorial-surface)',
										borderColor: 'var(--editorial-border)',
										color: type === t ? '#ffffff' : 'var(--editorial-text-secondary)'
									}}>
									{t ? typeLabels[t as keyof typeof typeLabels] : '全部'}
								</button>
							))}
						</div>
						{isAdmin &&
							(() => {
								const createAction = getCreateAction()
								return (
									<Uiv2Button href={createAction.href} className='ml-auto px-4 py-2 text-sm'>
										{createAction.label}
									</Uiv2Button>
								)
							})()}
					</div>

					{isAdmin && <SuggestionCard onExecuted={() => mutate()} defaultExpanded={showDashboard} />}
					{isAdmin && showDashboard && <WeeklySummaryCard />}

					{folderPath && (
						<div className='mb-4 flex items-center gap-1 text-sm' style={{ color: 'var(--editorial-text-secondary)' }}>
							<button
								type='button'
								onClick={() => handleFolderChange(null)}
								className='rounded px-1 transition-colors hover:bg-[var(--editorial-surface)] hover:text-[var(--editorial-text-primary)]'>
								全部
							</button>
							{folderPath.map((node, i) => (
								<span key={node.id} className='flex items-center gap-1'>
									<ChevronRight size={12} className='text-[var(--editorial-text-tertiary)]' />
									{i < folderPath.length - 1 ? (
										<button
											type='button'
											onClick={() => handleFolderChange(node.id)}
											className='rounded px-1 transition-colors hover:bg-[var(--editorial-surface)] hover:text-[var(--editorial-text-primary)]'>
											{node.name}
										</button>
									) : (
										<span className='font-medium text-[var(--editorial-text-primary)]'>{node.name}</span>
									)}
								</span>
							))}
							<button
								type='button'
								onClick={() => handleFolderChange(null)}
								aria-label='清除文件夹筛选'
								className='ml-1 rounded p-0.5 text-[var(--editorial-text-tertiary)] transition-colors hover:bg-[var(--editorial-surface)] hover:text-[var(--editorial-text-secondary)]'>
								<X size={12} />
							</button>
						</div>
					)}

					<div ref={resultRegionRef} tabIndex={-1} className='outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'>
					{renderState !== 'ready' ? (
						<AsyncStatePanel
							status={renderState}
							error={error}
							onRetry={retryNotes}
							loadingLabel='正在加载笔记'
							emptyHint={
								<EmptyState
									variant={activeFilter && activeFilter !== 'all' ? 'no-results' : 'no-content'}
									title={activeFilter && activeFilter !== 'all' ? '没有匹配结果' : '还没有笔记'}
									description={activeFilter && activeFilter !== 'all' ? '试试调整筛选条件' : emptyDescription}
									action={isAdmin ? getCreateAction() : null}
								/>
							}
						/>
					) : (
						<div role='region' aria-label='笔记结果' className='grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3'>
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
										className='block h-full rounded-xl border p-4 transition-shadow hover:shadow-md'
										style={{
											background: 'var(--editorial-surface)',
											borderColor: 'var(--editorial-border)',
											boxShadow: 'var(--ui-shadow-xs, 0 1px 2px rgba(0, 0, 0, 0.04))'
										}}>
										<div className='mb-2 flex items-center gap-2'>
											<span className='shrink-0'>
												<Uiv2Badge text={typeLabels[item.type]} tone={item.type} />
											</span>
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
													className='ml-auto shrink-0 rounded-md p-1 text-[var(--editorial-text-tertiary)] transition-colors hover:bg-[var(--editorial-surface-elevated)] hover:text-[var(--editorial-text-secondary)]'
													aria-label='移动到文件夹'>
													<MoreHorizontal size={14} />
												</button>
											)}
											<span className='shrink-0 text-xs' style={{ color: 'var(--editorial-text-tertiary)' }}>
												{dayjs(item.updated_at).format('YYYY-MM-DD')}
											</span>
										</div>
										<h3 className='truncate font-medium' style={{ color: 'var(--editorial-text-primary)' }}>
											{item.title}
										</h3>
										{item.summary && (
											<p className='mt-1 line-clamp-2 text-sm' style={{ color: 'var(--editorial-text-secondary)' }}>
												{item.summary}
											</p>
										)}
										{item.tags.length > 0 && (
											<div className='mt-2 flex flex-wrap gap-1'>
												{item.tags.map(tag => (
													<span
														key={tag.id}
														className='rounded px-1.5 py-0.5 text-xs'
														style={{ background: 'var(--editorial-surface-elevated)', color: 'var(--editorial-text-secondary)', border: '1px solid var(--editorial-divider)' }}>
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
					</div>

					{data && data.total > 20 && (
						<div className='mt-6 flex justify-center gap-2'>
							<Uiv2Button
								variant='ghost'
								disabled={page <= 1}
								onClick={() => setPage(p => p - 1)}
								className='text-sm'
								style={{ minHeight: 32, paddingLeft: 12, paddingRight: 12 }}>
								上一页
							</Uiv2Button>
							<span className='px-3 py-1 text-sm' style={{ color: 'var(--editorial-text-secondary)' }}>
								{page} / {Math.ceil(data.total / 20)}
							</span>
							<Uiv2Button
								variant='ghost'
								disabled={page >= Math.ceil(data.total / 20)}
								onClick={() => setPage(p => p + 1)}
								className='text-sm'
								style={{ minHeight: 32, paddingLeft: 12, paddingRight: 12 }}>
								下一页
							</Uiv2Button>
						</div>
					)}
				</div>
			</div>

			{ctxMenu && (
				<Uiv2ContextMenu
					open={!!ctxMenu}
					position={{ x: ctxMenu.x, y: ctxMenu.y }}
					onClose={() => setCtxMenu(null)}
					actions={getContextMenuItems().map((item, index) => ({
						id: `note-context-${index}`,
						label: item.label,
						icon: item.icon,
						variant: item.variant,
						disabled: item.disabled,
						run: item.onClick
					}))}
				/>
			)}

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
		</main>
	)
}
