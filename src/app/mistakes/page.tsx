'use client'

import { useState, useMemo, useRef } from 'react'
import Link from 'next/link'
import { motion } from 'motion/react'
import { useNoteIndex, useReviewPlan, useReviewStats } from '@/hooks/use-note-index'
import { cn } from '@/lib/utils'
import dayjs from 'dayjs'
import { KnowledgeSidebar } from '@/app/notes/components/knowledge-sidebar'
import { EmptyState } from '@/components/empty-state'
import { WeakPointDiagnosis } from './components/weak-point-diagnosis'
import { useAdminAuth } from '@/hooks/use-admin-auth'

const diffColors = { easy: 'bg-emerald-500/20 text-emerald-600', medium: 'bg-yellow-500/20 text-yellow-600', hard: 'bg-red-500/20 text-red-600' }
const diffLabels = { easy: '简单', medium: '中等', hard: '困难' }

export default function MistakesPage() {
	const [subject, setSubject] = useState('')
	const [difficulty, setDifficulty] = useState('')
	const [q, setQ] = useState('')
	const [page, setPage] = useState(1)
	const [activeFilter, setActiveFilter] = useState('all')
	const [activeFolderId, setActiveFolderId] = useState<string | null>(null)
	const [activeTag, setActiveTag] = useState<string | null>(null)
	const { isAdmin } = useAdminAuth()

	const { data, isLoading } = useNoteIndex({
		type: 'mistake',
		status: 'published',
		subject: subject || undefined,
		difficulty: (difficulty as any) || undefined,
		q: q || undefined,
		tag: activeTag || undefined,
		folder_id: activeFolderId || undefined,
		inbox: activeFilter === 'inbox' ? true : undefined,
		page,
		size: 20,
	})

	const { data: stats } = useReviewStats(isAdmin)
	const { data: plan } = useReviewPlan(isAdmin)

	const items = data?.items || []

	const tagsRef = useRef(new Map<number, { id: number; name: string }>())

	const pageTags = useMemo(() => {
		for (const item of items) {
			for (const tag of item.tags) {
				if (!tagsRef.current.has(tag.id)) tagsRef.current.set(tag.id, tag)
			}
		}
		return Array.from(tagsRef.current.values())
	}, [items])

	return (
		<div className='mx-auto max-w-6xl px-4 py-8'>
			<motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className='mb-6 text-2xl font-bold'>
				错题集
			</motion.h1>

			<div className='flex gap-6'>
			<KnowledgeSidebar
				mode='mistake'
				activeFilter={activeFilter}
				activeFolderId={activeFolderId}
				activeTag={activeTag}
				onFilterChange={setActiveFilter}
				onFolderChange={setActiveFolderId}
				onTagChange={setActiveTag}
				contentTypes={['mistake']}
				tags={pageTags}
			/>

				<div className='min-w-0 flex-1'>

			{isAdmin && stats && (
				<div className='mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4'>
					{[
						{ label: '总题数', value: stats.total_mistakes, color: 'text-gray-700' },
						{ label: '待复习', value: stats.pending_review, color: 'text-orange-500' },
						{ label: '今日到期', value: stats.due_today, color: 'text-red-500' },
						{ label: '已掌握', value: stats.mastered, color: 'text-green-500' },
					].map(s => (
						<div key={s.label} className='rounded-xl border border-white/40 bg-white/60 p-3 text-center backdrop-blur-sm'>
							<div className={cn('text-2xl font-bold', s.color)}>{s.value}</div>
							<div className='text-xs text-gray-500'>{s.label}</div>
						</div>
					))}
				</div>
			)}

			{isAdmin && plan && (
				<div className='mb-6 grid gap-3 lg:grid-cols-[1.1fr_0.9fr]'>
					<div className='rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm'>
						<div className='mb-3 flex items-center justify-between gap-3'>
							<div>
								<h2 className='text-sm font-semibold text-gray-800'>今日复习规划</h2>
								<p className='mt-0.5 text-xs text-gray-500'>
									{plan.today_count > 0 ? `今天有 ${plan.today_count} 道错题到期` : '今天没有到期错题'}
									{plan.overdue_count > 0 && `，其中 ${plan.overdue_count} 道已逾期`}
								</p>
							</div>
							<Link
								href='/mistakes/review'
								className='shrink-0 rounded-lg bg-orange-500 px-3 py-1.5 text-xs text-white transition-transform hover:scale-105 active:scale-95'
							>
								开始复习
							</Link>
						</div>
						<div className='grid grid-cols-3 gap-2 text-center'>
							<div className='rounded-lg bg-white/50 px-2 py-2'>
								<div className='text-lg font-semibold text-red-500'>{plan.today_count}</div>
								<div className='text-[11px] text-gray-500'>今日</div>
							</div>
							<div className='rounded-lg bg-white/50 px-2 py-2'>
								<div className='text-lg font-semibold text-orange-500'>{plan.week_count}</div>
								<div className='text-[11px] text-gray-500'>本周</div>
							</div>
							<div className='rounded-lg bg-white/50 px-2 py-2'>
								<div className='text-lg font-semibold text-gray-700'>{plan.next_review_date ? dayjs(plan.next_review_date).format('MM-DD') : '-'}</div>
								<div className='text-[11px] text-gray-500'>下次</div>
							</div>
						</div>
						{plan.recommendations.length > 0 && (
							<div className='mt-3 space-y-1.5'>
								{plan.recommendations.map(item => (
									<div key={item} className='rounded-lg bg-white/40 px-3 py-2 text-xs leading-5 text-gray-600'>
										{item}
									</div>
								))}
							</div>
						)}
					</div>

					<div className='rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm'>
						<h2 className='text-sm font-semibold text-gray-800'>薄弱点归总</h2>
						{plan.weaknesses.length > 0 ? (
							<div className='mt-3 space-y-2'>
								{plan.weaknesses.slice(0, 4).map(item => (
									<div key={item.name} className='flex items-center gap-2 rounded-lg bg-white/45 px-3 py-2 text-xs'>
										<span className='min-w-0 flex-1 truncate text-gray-700'>{item.name}</span>
										<span className='rounded-full bg-purple-500/15 px-2 py-0.5 text-purple-600'>{item.count} 次</span>
										{item.due_today > 0 && <span className='rounded-full bg-red-500/15 px-2 py-0.5 text-red-600'>到期 {item.due_today}</span>}
									</div>
								))}
							</div>
						) : (
								<p className='mt-3 rounded-lg bg-white/45 px-3 py-2 text-xs text-gray-500'>暂无可归总的知识点，后续错题补充知识点后会自动聚合。</p>
						)}
						{plan.subject_summaries.length > 0 && (
							<div className='mt-3 flex flex-wrap gap-1.5'>
								{plan.subject_summaries.slice(0, 4).map(item => (
									<span key={item.subject} className='rounded-full bg-gray-200/60 px-2 py-1 text-[11px] text-gray-600'>
										{item.subject}: {item.total} 题
									</span>
								))}
							</div>
						)}
					</div>
				</div>
			)}

			{isAdmin && (
				<div className='mb-6'>
					<WeakPointDiagnosis enabled={isAdmin} />
				</div>
			)}

			<div className='mb-6 flex flex-wrap items-center gap-3'>
				{isAdmin && (stats?.due_today ?? 0) > 0 && (
					<Link
						href='/mistakes/review'
						className='rounded-xl bg-orange-500 px-4 py-2 text-sm text-white transition-transform hover:scale-105 active:scale-95'
					>
						开始复习 ({stats?.due_today})
					</Link>
				)}
				<input
					value={q}
					onChange={e => { setQ(e.target.value); setPage(1) }}
					placeholder='搜索错题...'
					className='rounded-xl border border-white/40 bg-white/60 px-4 py-2 backdrop-blur-sm outline-none focus:border-[var(--color-brand)]'
				/>
				<select
					value={difficulty}
					onChange={e => { setDifficulty(e.target.value); setPage(1) }}
					className='rounded-lg border border-white/40 bg-white/60 px-3 py-2 text-sm outline-none'
				>
					<option value=''>全部难度</option>
					<option value='easy'>简单</option>
					<option value='medium'>中等</option>
					<option value='hard'>困难</option>
				</select>
				{isAdmin && (
					<Link
						href='/write-mistake'
						className='ml-auto rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white transition-transform hover:scale-105 active:scale-95'
					>
						添加错题
					</Link>
				)}
			</div>

			{isLoading ? (
				<div className='py-20 text-center text-gray-400'>加载中...</div>
			) : items.length === 0 ? (
				<div className='py-20'>
					<EmptyState
						variant='no-content'
						title='还没有错题'
						description={isAdmin ? '记录第一道错题，开始系统化复习' : '当前没有公开错题'}
						action={isAdmin ? { label: '添加错题', href: '/write-mistake' } : undefined}
					/>
				</div>
			) : (
				<div className='space-y-3'>
					{items.map((item, i) => (
						<motion.div
							key={item.id}
							initial={{ opacity: 0, y: 20 }}
							animate={{ opacity: 1, y: 0 }}
							transition={{ delay: i * 0.05 }}
						>
							<Link
								href={`/notes/${item.slug}`}
								className='block rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm transition-all hover:bg-white/80 hover:shadow-sm'
							>
								<div className='mb-2 flex items-center gap-2'>
									{item.difficulty && (
										<span className={cn('rounded-full px-2 py-0.5 text-xs', diffColors[item.difficulty])}>
											{diffLabels[item.difficulty]}
										</span>
									)}
								{item.subject && (
									<span className='max-w-[120px] truncate rounded-full bg-purple-500/20 px-2 py-0.5 text-xs text-purple-600'>
										{item.subject}
									</span>
								)}
									<span className='ml-auto text-xs text-gray-400'>
										{dayjs(item.created_at).format('YYYY-MM-DD')}
									</span>
								</div>
								<h3 className='truncate font-medium'>{item.title}</h3>
								{isAdmin && (
									<div className='mt-2 flex items-center gap-4 text-xs text-gray-500'>
										<span>复习 {item.repetitions || 0} 次</span>
										<span>EF {(item.ef || 2.5).toFixed(2)}</span>
										{item.next_review && (
											<span className={cn(
												dayjs(item.next_review).isBefore(dayjs(), 'day') ? 'text-red-500' : 'text-gray-500'
											)}>
												下次: {dayjs(item.next_review).format('MM-DD')}
											</span>
										)}
									</div>
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
							</Link>
						</motion.div>
					))}
				</div>
			)}
				</div>
			</div>
		</div>
	)
}
