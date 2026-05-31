'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'motion/react'
import { getReviewQueue, submitReview, getReviewStats, type ReviewStats } from '@/lib/api/review'
import type { NoteDetail } from '@/lib/api/notes'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

const qualityLabels = [
	{ q: 0, label: '完全忘记', color: 'bg-red-500' },
	{ q: 1, label: '有印象', color: 'bg-orange-500' },
	{ q: 2, label: '很熟悉', color: 'bg-yellow-500' },
	{ q: 3, label: '费力回忆', color: 'bg-lime-500' },
	{ q: 4, label: '略有犹豫', color: 'bg-green-500' },
	{ q: 5, label: '完美', color: 'bg-emerald-500' },
]

export default function ReviewPage() {
	const [queue, setQueue] = useState<NoteDetail[]>([])
	const [current, setCurrent] = useState(0)
	const [showAnswer, setShowAnswer] = useState(false)
	const [submitting, setSubmitting] = useState(false)
	const [done, setDone] = useState(false)
	const [reviewed, setReviewed] = useState(0)
	const [loading, setLoading] = useState(true)
	const [stats, setStats] = useState<ReviewStats | null>(null)

	useEffect(() => {
		Promise.all([getReviewQueue(), getReviewStats()]).then(([q, s]) => {
			setQueue(q)
			setStats(s)
			setLoading(false)
		})
	}, [])

	const item = queue[current]

	const handleReview = useCallback(async (quality: number) => {
		if (!item || submitting) return
		setSubmitting(true)
		try {
			await submitReview(item.slug, quality)
			setReviewed(r => r + 1)
			if (current + 1 >= queue.length) {
				setDone(true)
			} else {
				setCurrent(c => c + 1)
				setShowAnswer(false)
			}
		} catch (e: any) {
			toast.error('提交失败: ' + e.message)
		} finally {
			setSubmitting(false)
		}
	}, [item, submitting, current, queue.length])

	if (loading) return <div className='py-20 text-center text-gray-400'>加载复习队列...</div>

	if (queue.length === 0) {
		return (
			<div className='mx-auto max-w-xl px-4 py-20 text-center'>
				<motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
					<div className='mb-4 text-6xl'>🎉</div>
					<h2 className='mb-2 text-xl font-bold'>今日无待复习题目</h2>
					<p className='mb-6 text-gray-500'>所有错题都已复习完毕或暂无错题</p>
					<Link href='/mistakes' className='rounded-xl bg-[var(--color-brand)] px-6 py-2.5 text-sm text-white'>
						返回错题集
					</Link>
				</motion.div>
			</div>
		)
	}

	if (done) {
		return (
			<div className='mx-auto max-w-xl px-4 py-20 text-center'>
				<motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
					<div className='mb-4 text-6xl'>✅</div>
					<h2 className='mb-2 text-xl font-bold'>复习完成！</h2>
					<p className='mb-6 text-gray-500'>本次复习了 {reviewed} 道题</p>
					<Link href='/mistakes' className='rounded-xl bg-[var(--color-brand)] px-6 py-2.5 text-sm text-white'>
						返回错题集
					</Link>
				</motion.div>
			</div>
		)
	}

	return (
		<div className='mx-auto max-w-2xl px-4 py-8'>
			<div className='mb-6 flex items-center justify-between'>
				<Link href='/mistakes' className='text-sm text-gray-500 hover:text-gray-700'>← 返回</Link>
				<span className='text-sm text-gray-500'>{current + 1} / {queue.length}</span>
			</div>

			<div className='mb-4 h-1.5 overflow-hidden rounded-full bg-white/40'>
				<motion.div
					className='h-full bg-[var(--color-brand)]'
					initial={{ width: 0 }}
					animate={{ width: `${((current + (showAnswer ? 0.5 : 0)) / queue.length) * 100}%` }}
				/>
			</div>

			<AnimatePresence mode='wait'>
				<motion.div
					key={item.slug}
					initial={{ opacity: 0, x: 50 }}
					animate={{ opacity: 1, x: 0 }}
					exit={{ opacity: 0, x: -50 }}
					className='rounded-2xl border border-white/40 bg-white/60 p-6 backdrop-blur-sm'
				>
					<div className='mb-4 flex items-center gap-2'>
						{item.difficulty && (
							<span className={cn('rounded-full px-2 py-0.5 text-xs',
								item.difficulty === 'easy' ? 'bg-emerald-500/20 text-emerald-600' :
								item.difficulty === 'medium' ? 'bg-yellow-500/20 text-yellow-600' :
								'bg-red-500/20 text-red-600'
							)}>
								{{ easy: '简单', medium: '中等', hard: '困难' }[item.difficulty]}
							</span>
						)}
					{item.subject && (
						<span className='max-w-[120px] truncate rounded-full bg-purple-500/20 px-2 py-0.5 text-xs text-purple-600'>
							{item.subject}
						</span>
					)}
					</div>

					<h2 className='mb-4 truncate text-lg font-bold'>{item.title}</h2>

					{item.question && (
						<div className='mb-4 break-words whitespace-pre-wrap rounded-lg bg-gray-100/50 p-4 text-sm'>
							{item.question}
						</div>
					)}

					{!showAnswer ? (
						<button
							onClick={() => setShowAnswer(true)}
							className='w-full rounded-xl bg-[var(--color-brand)] py-3 text-sm text-white transition-transform hover:scale-[1.02] active:scale-[0.98]'
						>
							显示答案
						</button>
					) : (
						<motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
							{item.correct_answer && (
								<div className='mb-3'>
									<div className='mb-1 text-xs font-medium text-green-500'>正确答案</div>
									<div className='break-words whitespace-pre-wrap rounded-lg bg-green-50/50 p-3 text-sm'>{item.correct_answer}</div>
								</div>
							)}
							{item.analysis && (
								<div className='mb-3'>
									<div className='mb-1 text-xs font-medium text-blue-500'>分析</div>
									<div className='break-words whitespace-pre-wrap rounded-lg bg-blue-50/50 p-3 text-sm'>{item.analysis}</div>
								</div>
							)}
							{item.knowledge_points && (
								<div className='mb-4'>
									<div className='mb-1 text-xs font-medium text-purple-500'>知识点</div>
									<div className='break-words whitespace-pre-wrap rounded-lg bg-purple-50/50 p-3 text-sm'>{item.knowledge_points}</div>
								</div>
							)}

							<div className='text-center text-sm text-gray-500 mb-3'>你对这道题的掌握程度：</div>
							<div className='grid grid-cols-3 gap-2 sm:grid-cols-6'>
								{qualityLabels.map(({ q, label, color }) => (
									<button
										key={q}
										onClick={() => handleReview(q)}
										disabled={submitting}
										className={cn(
											'rounded-lg py-2 text-xs text-white transition-transform hover:scale-105 active:scale-95 disabled:opacity-50',
											color
										)}
									>
										{q}. {label}
									</button>
								))}
							</div>
						</motion.div>
					)}
				</motion.div>
			</AnimatePresence>
		</div>
	)
}
