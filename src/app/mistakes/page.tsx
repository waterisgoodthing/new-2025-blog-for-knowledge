'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'motion/react'
import { useNoteIndex, useReviewStats } from '@/hooks/use-note-index'
import { cn } from '@/lib/utils'
import dayjs from 'dayjs'

const diffColors = { easy: 'bg-emerald-500/20 text-emerald-600', medium: 'bg-yellow-500/20 text-yellow-600', hard: 'bg-red-500/20 text-red-600' }
const diffLabels = { easy: '简单', medium: '中等', hard: '困难' }

export default function MistakesPage() {
	const [subject, setSubject] = useState('')
	const [difficulty, setDifficulty] = useState('')
	const [q, setQ] = useState('')
	const [page, setPage] = useState(1)

	const { data, isLoading } = useNoteIndex({
		type: 'mistake',
		status: 'published',
		subject: subject || undefined,
		difficulty: (difficulty as any) || undefined,
		q: q || undefined,
		page,
		size: 20,
	})

	const { data: stats } = useReviewStats()

	const items = data?.items || []

	return (
		<div className='mx-auto max-w-4xl px-4 py-8'>
			<motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className='mb-6 text-2xl font-bold'>
				错题集
			</motion.h1>

			{stats && (
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

			<div className='mb-6 flex flex-wrap items-center gap-3'>
				{(stats?.due_today ?? 0) > 0 && (
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
				<Link
					href='/write-mistake'
					className='ml-auto rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white transition-transform hover:scale-105 active:scale-95'
				>
					添加错题
				</Link>
			</div>

			{isLoading ? (
				<div className='py-20 text-center text-gray-400'>加载中...</div>
			) : items.length === 0 ? (
				<div className='py-20 text-center text-gray-400'>暂无错题</div>
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
	)
}
