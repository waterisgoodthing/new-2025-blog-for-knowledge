'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { Sparkles, X, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { streamPolish } from '@/lib/api/ai-polish'

type TagSuggestionDialogProps = {
	open: boolean
	content: string
	title: string
	existingTags: string[]
	onApply: (tags: string[]) => void
	onSkip: () => void
	onDontRemind: () => void
}

export function TagSuggestionDialog({ open, content, title, existingTags, onApply, onSkip, onDontRemind }: TagSuggestionDialogProps) {
	const [loading, setLoading] = useState(false)
	const [suggestedTags, setSuggestedTags] = useState<string[]>([])
	const [error, setError] = useState('')
	const abortRef = useRef<AbortController | null>(null)
	const requestIdRef = useRef(0)
	const rafRef = useRef(0)

	useEffect(() => {
		if (open) {
			setSuggestedTags([])
			setError('')
			setLoading(false)
		}
		return () => {
			++requestIdRef.current
			abortRef.current?.abort()
			if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = 0 }
		}
	}, [open])

	const generateTags = async () => {
		abortRef.current?.abort()
		const controller = new AbortController()
		abortRef.current = controller
		const currentId = ++requestIdRef.current

		setLoading(true)
		setError('')
		let accumulated = ''

		await streamPolish(content || title || '无内容', 'tags', {
			onChunk: chunk => {
				if (currentId !== requestIdRef.current) return
				accumulated += chunk
				if (!rafRef.current) {
					rafRef.current = requestAnimationFrame(() => { rafRef.current = 0 })
				}
			},
			onDone: () => {
				if (currentId !== requestIdRef.current) return
				if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = 0 }
				try {
					let cleaned = accumulated.trim()
					const fenceMatch = cleaned.match(/^```(?:json)?\s*\n?([\s\S]*?)\n?```$/)
					if (fenceMatch) cleaned = fenceMatch[1].trim()
					const parsed = JSON.parse(cleaned)
					const tags = Array.isArray(parsed) ? parsed.map(String) : []
					setSuggestedTags(tags.filter((t: string) => !existingTags.includes(t)))
				} catch {
					const lines = accumulated.split(/[\n,]/).map(s => s.trim().replace(/^[-*•\d.]+\s*/, '')).filter(Boolean)
					setSuggestedTags(lines.filter(t => !existingTags.includes(t)))
				}
				setLoading(false)
				abortRef.current = null
			},
			onError: err => {
				if (currentId !== requestIdRef.current) return
				if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = 0 }
				setError(err)
				setLoading(false)
				abortRef.current = null
			},
		}, {
			signal: controller.signal,
		})
	}

	if (!open) return null

	return (
		<AnimatePresence>
			<motion.div
				initial={{ opacity: 0 }}
				animate={{ opacity: 1 }}
				exit={{ opacity: 0 }}
				className='fixed inset-0 z-50 flex items-center justify-center bg-black/30'
				onClick={e => { if (e.target === e.currentTarget) onSkip() }}
			>
				<motion.div
					initial={{ scale: 0.95, opacity: 0 }}
					animate={{ scale: 1, opacity: 1 }}
					exit={{ scale: 0.95, opacity: 0 }}
					className='w-full max-w-sm rounded-2xl border border-white/40 bg-white/95 p-6 shadow-xl backdrop-blur-xl'
				>
					<div className='mb-4 flex items-center gap-2'>
						<Sparkles size={18} className='text-[var(--color-brand)]' />
						<h3 className='text-sm font-semibold text-gray-800'>还没有添加标签</h3>
					</div>
					<p className='mb-4 text-xs text-gray-500'>
						标签可以帮助你更好地组织和查找内容。是否让 AI 根据内容自动生成标签？
					</p>

					{error && (
						<div className='mb-3 rounded-lg bg-red-50/50 p-2 text-xs text-red-500'>{error}</div>
					)}

					{suggestedTags.length > 0 && (
						<div className='mb-4 flex flex-wrap gap-1.5'>
							{suggestedTags.map(tag => (
								<span key={tag} className='rounded-full bg-[var(--color-brand)]/10 px-2.5 py-1 text-xs text-[var(--color-brand)]'>
									{tag}
								</span>
							))}
						</div>
					)}

					<div className='flex flex-col gap-2'>
						{!loading && suggestedTags.length === 0 && (
							<button
								type='button'
								onClick={generateTags}
								className='flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--color-brand)] px-4 py-2.5 text-sm font-medium text-white transition-transform hover:scale-[1.02] active:scale-95'
							>
								<Sparkles size={14} />
								生成标签建议
							</button>
						)}
						{loading && (
							<div className='flex items-center justify-center gap-2 py-2 text-xs text-gray-400'>
								<Loader2 size={14} className='animate-spin' />
								正在分析内容生成标签...
							</div>
						)}
						{suggestedTags.length > 0 && (
							<button
								type='button'
								onClick={() => { onApply(suggestedTags) }}
								className='flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--color-brand)] px-4 py-2.5 text-sm font-medium text-white transition-transform hover:scale-[1.02] active:scale-95'
							>
								使用这些标签继续保存
							</button>
						)}
						<button
							type='button'
							onClick={onSkip}
							className='rounded-xl bg-white/60 px-4 py-2.5 text-sm text-gray-600 hover:bg-white/80'
						>
							暂不添加标签
						</button>
					</div>
					<div className='mt-4 text-left'>
						<button
							type='button'
							onClick={onDontRemind}
							className='text-xs text-gray-400 hover:text-gray-600'
						>
							下次不再提醒
						</button>
					</div>
				</motion.div>
			</motion.div>
		</AnimatePresence>
	)
}
