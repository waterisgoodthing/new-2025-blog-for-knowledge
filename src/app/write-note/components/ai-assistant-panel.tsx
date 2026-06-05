'use client'

import { useState, useRef, useEffect, type RefObject } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { ChevronLeft, ChevronRight, Square, RefreshCw, Copy, ArrowDown, Replace, Type, Tags, FileText, Sparkles } from 'lucide-react'
import { toast } from 'sonner'
import { streamPolish, type PolishAction } from '@/lib/api/ai-polish'

function useIsMobile() {
	const [isMobile, setIsMobile] = useState(false)
	useEffect(() => {
		const mq = window.matchMedia('(max-width: 768px)')
		setIsMobile(mq.matches)
		const handler = (e: MediaQueryListEvent) => setIsMobile(e.matches)
		mq.addEventListener('change', handler)
		return () => mq.removeEventListener('change', handler)
	}, [])
	return isMobile
}

type AIActionGroup = {
	label: string
	actions: { id: PolishAction; label: string }[]
}

const actionGroups: AIActionGroup[] = [
	{
		label: '选区操作',
		actions: [
			{ id: 'polish', label: '改写' },
			{ id: 'expand', label: '扩写' },
			{ id: 'summarize', label: '总结' },
			{ id: 'continue', label: '续写' },
		],
	},
	{
		label: '插入内容',
		actions: [
			{ id: 'diagram', label: '图表' },
			{ id: 'compare', label: '对比块' },
			{ id: 'mindmap', label: '思维导图' },
			{ id: 'data_chart', label: '数据分析' },
		],
	},
	{
		label: '全文处理',
		actions: [
			{ id: 'title', label: '生成标题' },
			{ id: 'outline', label: '生成目录' },
			{ id: 'tags', label: '推荐标签' },
		],
	},
]

type ActionMeta = {
	action: PolishAction
	label: string
}

type AIAssistantPanelProps = {
	textareaRef: RefObject<HTMLTextAreaElement | null>
	content: string
	title?: string
	noteType?: string
	existingTags?: string[]
	onInsert: (text: string) => void
	onReplaceSelection: (text: string) => void
	getSelectedText: () => string
	onApplyTitle?: (title: string) => void
	onApplySummary?: (summary: string) => void
	onApplyTags?: (tags: string[]) => void
}

export function AIAssistantPanel({
	textareaRef, content, title, noteType, existingTags,
	onInsert, onReplaceSelection, getSelectedText,
	onApplyTitle, onApplySummary, onApplyTags,
}: AIAssistantPanelProps) {
	const [expanded, setExpanded] = useState(false)
	const [loading, setLoading] = useState(false)
	const [result, setResult] = useState('')
	const [error, setError] = useState('')
	const [lastAction, setLastAction] = useState<ActionMeta | null>(null)
	const abortRef = useRef<AbortController | null>(null)
	const requestIdRef = useRef(0)
	const isMobile = useIsMobile()

	useEffect(() => {
		return () => { abortRef.current?.abort() }
	}, [])

	const runAction = async (action: PolishAction, label: string) => {
		const selected = getSelectedText()
		const text = selected || content

		if (!text.trim()) {
			toast.warning('请先输入内容')
			return
		}

		abortRef.current?.abort()
		const controller = new AbortController()
		abortRef.current = controller
		const currentId = ++requestIdRef.current

		setLoading(true)
		setResult('')
		setError('')
		setLastAction({ action, label })

		let accumulated = ''

		await streamPolish(text, action, {
			onChunk: chunk => {
				if (currentId !== requestIdRef.current) return
				accumulated += chunk
				setResult(accumulated)
			},
			onDone: () => {
				if (currentId !== requestIdRef.current) return
				setLoading(false)
				abortRef.current = null
			},
			onError: err => {
				if (currentId !== requestIdRef.current) return
				setError(err)
				setLoading(false)
				abortRef.current = null
			},
		}, {
			context: selected ? content : undefined,
			signal: controller.signal,
			title,
			noteType,
			existingTags,
		})
	}

	const handleStop = () => {
		abortRef.current?.abort()
		abortRef.current = null
		setLoading(false)
	}

	const handleClose = () => {
		handleStop()
		setExpanded(false)
	}

	const handleCopy = async () => {
		try {
			await navigator.clipboard.writeText(result)
			toast.success('已复制')
		} catch {
			toast.error('复制失败')
		}
	}

	const handleInsert = () => {
		let wrapped = result
		if (lastAction?.action === 'mindmap') {
			wrapped = '\n```markmap\n' + result.trim() + '\n```'
		} else if (lastAction?.action === 'data_chart') {
			wrapped = '\n```chart\n' + result.trim() + '\n```'
		}
		onInsert('\n\n' + wrapped)
		toast.success('已插入')
	}

	const handleReplace = () => {
		onReplaceSelection(result)
		toast.success('已替换')
	}

	const handleApplyTitle = () => {
		onApplyTitle?.(result.trim())
		toast.success('已应用为标题')
	}

	const handleApplyTags = () => {
		try {
			let cleaned = result.trim()
			// Strip ```json ... ``` fences if present
			const fenceMatch = cleaned.match(/^```(?:json)?\s*\n?([\s\S]*?)\n?```$/)
			if (fenceMatch) cleaned = fenceMatch[1].trim()
			const parsed = JSON.parse(cleaned)
			if (Array.isArray(parsed)) {
				onApplyTags?.(parsed.map(String))
				toast.success('已合并标签')
			} else {
				onInsert('\n\n' + result)
			}
		} catch {
			onInsert('\n\n' + result)
		}
	}

	const handleApplySummary = () => {
		onApplySummary?.(result.trim())
		toast.success('已应用为摘要')
	}

	const panelContent = (
		<div className='flex h-full flex-col'>
			<div className='flex items-center justify-between border-b border-white/40 p-3'>
				<span className='text-sm font-medium'>AI 助手</span>
				<button type='button' onClick={handleClose} className='text-gray-400 hover:text-gray-600' aria-label='关闭 AI 助手' title='关闭 AI 助手'>
					{isMobile ? <Square size={16} /> : <ChevronRight size={16} />}
				</button>
			</div>

			<div className='space-y-3 p-3'>
				{actionGroups.map(group => (
					<div key={group.label}>
						<div className='mb-1.5 text-[11px] font-medium text-gray-400'>{group.label}</div>
						<div className={isMobile ? 'flex gap-1.5 overflow-x-auto pb-1' : 'flex flex-wrap gap-1.5'}>
							{group.actions.map(a => (
								<button
									key={a.id}
									type='button'
									onClick={() => runAction(a.id, a.label)}
									disabled={loading}
									className='shrink-0 rounded-lg bg-white/60 px-2.5 py-1 text-xs transition-colors hover:bg-white/80 disabled:opacity-40'>
									{a.label}
								</button>
							))}
						</div>
					</div>
				))}
			</div>

			<div className='flex-1 overflow-y-auto px-3 pb-3'>
				{loading && !result && (
					<div className='space-y-2'>
						<div className='h-4 animate-pulse rounded bg-gray-200/60' />
						<div className='h-4 w-3/4 animate-pulse rounded bg-gray-200/60' />
						<div className='h-4 w-1/2 animate-pulse rounded bg-gray-200/60' />
					</div>
				)}

				{error && (
					<div className='rounded-lg bg-red-50/50 p-3 text-xs text-red-600'>
						{error}
						<button type='button' onClick={() => { setError(''); setResult('') }} className='ml-2 text-red-400 hover:text-red-600'>
							<RefreshCw size={12} />
						</button>
					</div>
				)}

				{result && (
					<div className='min-h-[120px] rounded-lg border border-white/40 bg-white/40 p-3 text-sm whitespace-pre-wrap'>
						{result}
					</div>
				)}
			</div>

			{result && !loading && (
				<div className='flex flex-wrap gap-1.5 border-t border-white/40 p-3'>
					{lastAction?.action === 'title' && onApplyTitle && (
						<button type='button' onClick={handleApplyTitle} className='flex items-center gap-1 rounded-lg bg-[var(--color-brand)]/10 px-2.5 py-1.5 text-xs text-[var(--color-brand)] hover:bg-[var(--color-brand)]/20'>
							<Type size={12} /> 应用为标题
						</button>
					)}
					{lastAction?.action === 'tags' && onApplyTags && (
						<button type='button' onClick={handleApplyTags} className='flex items-center gap-1 rounded-lg bg-[var(--color-brand)]/10 px-2.5 py-1.5 text-xs text-[var(--color-brand)] hover:bg-[var(--color-brand)]/20'>
							<Tags size={12} /> 合并标签
						</button>
					)}
					{lastAction?.action === 'summarize' && onApplySummary && (
						<button type='button' onClick={handleApplySummary} className='flex items-center gap-1 rounded-lg bg-[var(--color-brand)]/10 px-2.5 py-1.5 text-xs text-[var(--color-brand)] hover:bg-[var(--color-brand)]/20'>
							<FileText size={12} /> 应用为摘要
						</button>
					)}
					<button type='button' onClick={handleInsert} className='flex items-center gap-1 rounded-lg bg-white/60 px-2.5 py-1.5 text-xs hover:bg-white/80'>
						<ArrowDown size={12} /> 插入
					</button>
					<button type='button' onClick={handleReplace} className='flex items-center gap-1 rounded-lg bg-white/60 px-2.5 py-1.5 text-xs hover:bg-white/80'>
						<Replace size={12} /> 替换
					</button>
					<button type='button' onClick={handleCopy} className='flex items-center gap-1 rounded-lg bg-white/60 px-2.5 py-1.5 text-xs hover:bg-white/80'>
						<Copy size={12} /> 复制
					</button>
				</div>
			)}

			{loading && (
				<div className='border-t border-white/40 p-3'>
					<button type='button' onClick={handleStop} className='flex w-full items-center justify-center gap-1 rounded-lg bg-red-50/50 px-2.5 py-1.5 text-xs text-red-600 hover:bg-red-100/50'>
						<Square size={12} /> 停止生成
					</button>
				</div>
			)}
		</div>
	)

	if (isMobile) {
		return (
			<>
				<AnimatePresence>
					{expanded && (
						<>
							<motion.div
								initial={{ opacity: 0 }}
								animate={{ opacity: 1 }}
								exit={{ opacity: 0 }}
								className='fixed inset-0 z-40 bg-black/20'
								onClick={handleClose}
							/>
							<motion.div
								initial={{ y: '100%' }}
								animate={{ y: 0 }}
								exit={{ y: '100%' }}
								transition={{ type: 'spring', damping: 25, stiffness: 300 }}
								className='fixed inset-x-0 bottom-0 z-50 max-h-[70vh] rounded-t-2xl border-t border-white/40 bg-white/95 backdrop-blur-xl'
							>
								<div className='mx-auto my-2 h-1 w-10 rounded-full bg-gray-300' />
								{panelContent}
							</motion.div>
						</>
					)}
				</AnimatePresence>
				<button
					type='button'
					onClick={() => setExpanded(true)}
					className='flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl border border-white/40 bg-white/60 text-gray-500 backdrop-blur-sm transition-colors hover:bg-white/80 hover:text-[var(--color-brand)]'
					aria-label='打开 AI 助手'
					title='AI 助手'>
					<Sparkles size={16} />
				</button>
			</>
		)
	}

	return (
		<div className='flex'>
			<AnimatePresence>
				{expanded && (
					<motion.div
						initial={{ width: 0, opacity: 0 }}
						animate={{ width: 320, opacity: 1 }}
						exit={{ width: 0, opacity: 0 }}
						transition={{ duration: 0.2 }}
						className='overflow-hidden'>
						<div className='ml-2 flex h-full w-80 flex-col rounded-xl border border-white/40 bg-white/60 backdrop-blur-sm'>
							{panelContent}
						</div>
					</motion.div>
				)}
			</AnimatePresence>

			{!expanded && (
				<button
					type='button'
					onClick={() => setExpanded(true)}
					className='ml-2 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl border border-white/40 bg-white/60 text-gray-500 backdrop-blur-sm transition-colors hover:bg-white/80 hover:text-[var(--color-brand)]'
					aria-label='打开 AI 助手'
					title='AI 助手'>
					<ChevronLeft size={16} />
				</button>
			)}
		</div>
	)
}
