'use client'

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import { motion } from 'motion/react'
import dayjs from 'dayjs'
import {
	listPublicMistakes,
	type PublicMistake,
	type PublicMistakeListResponse,
	type MistakeReason,
} from '@/lib/api/mistakes'
import { AsyncStatePanel } from '@/components/async-state-panel'
import { useReviewPlan, useReviewStats } from '@/hooks/use-note-index'
import { cn } from '@/lib/utils'
import { WeakPointDiagnosis } from './components/weak-point-diagnosis'
import { useAdminAuth } from '@/hooks/use-admin-auth'

const diffColors = { easy: 'bg-emerald-500/20 text-emerald-600', medium: 'bg-yellow-500/20 text-yellow-600', hard: 'bg-red-500/20 text-red-600' }
const diffLabels = { easy: '简单', medium: '中等', hard: '困难' }
const reasonLabels: Record<MistakeReason, string> = {
	concept: '概念理解',
	calculation: '计算过程',
	reading: '审题阅读',
	careless: '粗心失误',
	unknown: '未分类',
}

const PAGE_SIZE = 20

export default function MistakesPage() {
	const [page, setPage] = useState(1)
	const [data, setData] = useState<PublicMistakeListResponse | null>(null)
	const [error, setError] = useState<unknown>(null)
	const [isLoading, setIsLoading] = useState(true)
	const [reloadKey, setReloadKey] = useState(0)
	const { isAdmin } = useAdminAuth({ mode: 'optional' })

	const { data: stats } = useReviewStats(isAdmin)
	const { data: plan } = useReviewPlan(isAdmin)

	useEffect(() => {
		let cancelled = false
		setIsLoading(true)
		setError(null)
		listPublicMistakes({ page, size: PAGE_SIZE })
			.then((response) => {
				if (!cancelled) setData(response)
			})
			.catch((reason: unknown) => {
				if (!cancelled) {
					setData(null)
					setError(reason)
				}
			})
			.finally(() => {
				if (!cancelled) setIsLoading(false)
			})
		return () => {
			cancelled = true
		}
	}, [page, reloadKey])

	const retry = useCallback(() => {
		setReloadKey((key) => key + 1)
	}, [])

	const items = data?.items ?? []
	const renderState: 'loading' | 'error' | 'empty' | 'ready' = isLoading
		? 'loading'
		: error
			? 'error'
			: (data?.empty || items.length === 0)
				? 'empty'
				: 'ready'
	const totalPages = data ? Math.max(1, Math.ceil(data.total / (data.size || PAGE_SIZE))) : 1

	return (
		<div className='mx-auto max-w-6xl px-4 py-8' data-render-state={renderState}>
			<motion.h1 initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className='mb-6 text-2xl font-bold'>
				错题集
			</motion.h1>

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
								href='/manage/review'
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
						href='/manage/review'
						className='rounded-xl bg-orange-500 px-4 py-2 text-sm text-white transition-transform hover:scale-105 active:scale-95'
					>
						开始复习 ({stats?.due_today})
					</Link>
				)}
				{data && !data.empty && (
					<span className='text-sm text-gray-500'>共 {data.total} 道公开错题</span>
				)}
				{isAdmin && (
					<Link
						href='/manage/capture'
						className='ml-auto rounded-xl bg-[var(--color-brand)] px-4 py-2 text-sm text-white transition-transform hover:scale-105 active:scale-95'
					>
						添加错题
					</Link>
				)}
			</div>

			{renderState !== 'ready' ? (
				<AsyncStatePanel
					status={renderState}
					error={error}
					onRetry={retry}
					loadingLabel='正在加载公开错题'
					emptyHint={data?.message || '当前没有公开错题'}
				/>
			) : (
				<div role='region' aria-label='公开错题列表' className='space-y-3'>
					{items.map((item, i) => (
						<PublicMistakeCard key={item.id} item={item} index={i} />
					))}
				</div>
			)}

			{renderState === 'ready' && totalPages > 1 && (
				<div className='mt-6 flex justify-center gap-2'>
					<button
						type='button'
						disabled={page <= 1}
						onClick={() => setPage((p) => Math.max(1, p - 1))}
						className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'
					>
						上一页
					</button>
					<span className='px-3 py-1 text-sm text-gray-500'>{page} / {totalPages}</span>
					<button
						type='button'
						disabled={page >= totalPages}
						onClick={() => setPage((p) => p + 1)}
						className='rounded-lg bg-white/60 px-3 py-1 text-sm disabled:opacity-40'
					>
						下一页
					</button>
				</div>
			)}
		</div>
	)
}

function PublicMistakeCard({ item, index }: { item: PublicMistake; index: number }) {
	return (
		<motion.article
			initial={{ opacity: 0, y: 20 }}
			animate={{ opacity: 1, y: 0 }}
			transition={{ delay: index * 0.05 }}
			className='rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm'
		>
			<div className='mb-2 flex flex-wrap items-center gap-2'>
				{item.difficulty && (
					<span className={cn('rounded-full px-2 py-0.5 text-xs', diffColors[item.difficulty])}>
						{diffLabels[item.difficulty]}
					</span>
				)}
				<span className='rounded-full bg-purple-500/20 px-2 py-0.5 text-xs text-purple-600'>
					{reasonLabels[item.reason_category] ?? item.reason_category}
				</span>
				<span className='ml-auto text-xs text-gray-400'>
					{dayjs(item.created_at).format('YYYY-MM-DD')}
					{item.updated_at !== item.created_at && ` · 更新 ${dayjs(item.updated_at).format('YYYY-MM-DD')}`}
				</span>
			</div>

			<h2 className='text-base font-medium text-gray-900'>{item.title || '未命名错题'}</h2>

			{item.question_text && (
				<section className='mt-3'>
					<h3 className='text-xs font-semibold text-gray-500'>题目</h3>
					<p className='mt-1 whitespace-pre-wrap text-sm leading-6 text-gray-700'>{item.question_text}</p>
				</section>
			)}

			{item.correct_answer && (
				<section className='mt-3'>
					<h3 className='text-xs font-semibold text-gray-500'>正确答案</h3>
					<p className='mt-1 whitespace-pre-wrap text-sm leading-6 text-gray-700'>{item.correct_answer}</p>
				</section>
			)}

			{item.analysis && (
				<section className='mt-3'>
					<h3 className='text-xs font-semibold text-gray-500'>解析</h3>
					<p className='mt-1 whitespace-pre-wrap text-sm leading-6 text-gray-700'>{item.analysis}</p>
				</section>
			)}

			{item.mistake_reason && (
				<section className='mt-3'>
					<h3 className='text-xs font-semibold text-gray-500'>错因说明</h3>
					<p className='mt-1 whitespace-pre-wrap text-sm leading-6 text-gray-700'>{item.mistake_reason}</p>
				</section>
			)}

			{item.knowledge_point_ids.length > 0 && (
				<div className='mt-3 flex flex-wrap gap-1'>
					{item.knowledge_point_ids.map((id) => (
						<span key={id} className='rounded bg-gray-200/60 px-1.5 py-0.5 text-xs text-gray-500'>
							KP #{id}
						</span>
					))}
				</div>
			)}
		</motion.article>
	)
}
