'use client'

import Link from 'next/link'
import { useState } from 'react'
import { motion } from 'motion/react'
import { MoreHorizontal, GripVertical } from 'lucide-react'
import { useNoteIndex } from '@/hooks/use-note-index'
import { cn } from '@/lib/utils'
import dayjs from 'dayjs'
import { KnowledgeSidebar } from './components/knowledge-sidebar'
import { SuggestionCard } from './components/suggestion-card'
import { WeeklySummaryCard } from './components/weekly-summary-card'
import { MoveToFolderDialog } from '@/components/move-to-folder-dialog'
import { moveNoteToFolder } from '@/lib/api/folders'
import { toast } from 'sonner'

const typeLabels = { note: '笔记', blog: '博客', mistake: '错题' }
const typeColors = { note: 'bg-blue-500/20 text-blue-600', blog: 'bg-green-500/20 text-green-600', mistake: 'bg-red-500/20 text-red-600' }
const diffColors = { easy: 'bg-emerald-500/20 text-emerald-600', medium: 'bg-yellow-500/20 text-yellow-600', hard: 'bg-red-500/20 text-red-600' }

export default function NotesPage() {
	const [type, setType] = useState<string>('')
	const [q, setQ] = useState('')
	const [page, setPage] = useState(1)
	const [activeFilter, setActiveFilter] = useState('all')
	const [activeFolderId, setActiveFolderId] = useState<string | null>(null)
	const [activeTag, setActiveTag] = useState<string | null>(null)
	const [moveTarget, setMoveTarget] = useState<{ slug: string; title: string } | null>(null)
	const [draggingSlug, setDraggingSlug] = useState<string | null>(null)
	const [dragOverFolderId, setDragOverFolderId] = useState<string | null>(null)

	const handleDropToFolder = async (folderId: string | null) => {
		if (!draggingSlug) return
		try {
			await moveNoteToFolder(draggingSlug, folderId)
			toast.success(folderId ? '已移动到文件夹' : '已移回收件箱')
			mutate()
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

	const { data, isLoading, mutate } = useNoteIndex({
		type: type as any || undefined,
		status: 'published',
		q: q || undefined,
		tag: activeTag || undefined,
		folder_id: activeFolderId || undefined,
		inbox: activeFilter === 'inbox' ? true : undefined,
		page,
		size: 20,
	})

	return (
		<div className='mx-auto max-w-6xl px-4 py-8'>
			<motion.h1
				initial={{ opacity: 0, y: -20 }}
				animate={{ opacity: 1, y: 0 }}
				className='mb-6 text-2xl font-bold'
			>
				笔记
			</motion.h1>

			<div className='flex gap-6'>
				<KnowledgeSidebar
					activeFilter={activeFilter}
					activeFolderId={activeFolderId}
					activeTag={activeTag}
					onFilterChange={handleFilterChange}
					onFolderChange={setActiveFolderId}
					onTagChange={setActiveTag}
					onDropNote={handleDropToFolder}
					dragOverFolderId={dragOverFolderId}
					onDragOverFolderChange={setDragOverFolderId}
				/>

				<div className='min-w-0 flex-1'>

			<div className='mb-6 flex flex-wrap items-center gap-3'>
				<input
					value={q}
					onChange={e => { setQ(e.target.value); setPage(1) }}
					placeholder='搜索...'
					className='rounded-xl border border-white/40 bg-white/60 px-4 py-2 backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
				/>
				<div className='flex gap-2'>
					{['', 'note', 'blog', 'mistake'].map(t => (
						<button
							key={t}
							onClick={() => { setType(t); setPage(1) }}
							className={cn(
								'rounded-full px-3 py-1 text-sm transition-colors',
								type === t ? 'bg-[var(--color-brand)] text-white' : 'bg-white/60 hover:bg-white/80'
							)}
						>
							{t ? typeLabels[t as keyof typeof typeLabels] : '全部'}
						</button>
					))}
				</div>
				<Link
					href='/write-note'
					className='ml-auto rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white transition-transform hover:scale-105 active:scale-95'
				>
					写笔记
				</Link>
			</div>

			<SuggestionCard onExecuted={() => mutate()} />
			<WeeklySummaryCard />

			{isLoading ? (
				<div className='py-20 text-center text-gray-400'>加载中...</div>
			) : data?.items.length === 0 ? (
				<div className='py-20 text-center text-gray-400'>暂无内容</div>
			) : (
				<div className='space-y-3'>
					{data?.items.map((item, i) => (
						<motion.div
							key={item.id}
							initial={{ opacity: 0, y: 20 }}
							animate={{ opacity: 1, y: 0 }}
							transition={{ delay: i * 0.05 }}
							draggable
							onDragStart={() => setDraggingSlug(item.slug)}
							onDragEnd={() => { setDraggingSlug(null); setDragOverFolderId(null) }}
							className={cn(draggingSlug === item.slug && 'opacity-50')}
						>
							<Link
								href={`/notes/${item.slug}`}
								className='block rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm transition-all hover:bg-white/80 hover:shadow-sm'
							>
								<div className='mb-2 flex items-center gap-2'>
									<span className={cn('rounded-full px-2 py-0.5 text-xs', typeColors[item.type])}>
										{typeLabels[item.type]}
									</span>
									{item.difficulty && (
										<span className={cn('rounded-full px-2 py-0.5 text-xs', diffColors[item.difficulty])}>
											{item.difficulty}
										</span>
									)}
								{item.subject && (
									<span className='max-w-[120px] truncate rounded-full bg-purple-500/20 px-2 py-0.5 text-xs text-purple-600'>
										{item.subject}
									</span>
								)}
									<button
										type='button'
										onClick={e => { e.preventDefault(); e.stopPropagation(); setMoveTarget({ slug: item.slug, title: item.title }) }}
										className='ml-auto shrink-0 rounded-md p-1 text-gray-400 transition-colors hover:bg-white/60 hover:text-gray-600'
										aria-label='移动到文件夹'
									>
										<MoreHorizontal size={14} />
									</button>
									<span className='shrink-0 text-xs text-gray-400'>
										{dayjs(item.updated_at).format('YYYY-MM-DD')}
									</span>
								</div>
								<h3 className='truncate font-medium'>{item.title}</h3>
								{item.summary && (
									<p className='mt-1 line-clamp-2 text-sm text-gray-500'>{item.summary}</p>
								)}
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
									<div className='mt-2 text-xs text-orange-500'>
										下次复习: {dayjs(item.next_review).format('YYYY-MM-DD')}
									</div>
								)}
							</Link>
						</motion.div>
					))}
				</div>
			)}

			{data && data.total > 20 && (
				<div className='mt-6 flex justify-center gap-2'>
					<button
						disabled={page <= 1}
						onClick={() => setPage(p => p - 1)}
						className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'
					>
						上一页
					</button>
					<span className='px-3 py-1 text-sm text-gray-500'>
						{page} / {Math.ceil(data.total / 20)}
					</span>
					<button
						disabled={page >= Math.ceil(data.total / 20)}
						onClick={() => setPage(p => p + 1)}
						className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'
					>
						下一页
					</button>
				</div>
			)}
				</div>
			</div>

			{moveTarget && (
				<MoveToFolderDialog
					slug={moveTarget.slug}
					noteTitle={moveTarget.title}
					open={!!moveTarget}
					onClose={() => setMoveTarget(null)}
					onMoved={() => { mutate(); setMoveTarget(null) }}
				/>
			)}
		</div>
	)
}
