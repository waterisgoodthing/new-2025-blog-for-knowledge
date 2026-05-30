'use client'

import { useState, useRef, type RefObject } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { Sparkles, ChevronLeft, ChevronRight, Square, RefreshCw, Copy, ArrowDown, Replace } from 'lucide-react'
import { toast } from 'sonner'
import { streamPolish, type PolishAction } from '@/lib/api/ai-polish'

type AIAction = {
	id: PolishAction
	label: string
}

const aiActions: AIAction[] = [
	{ id: 'polish', label: '润色' },
	{ id: 'summarize', label: '总结' },
	{ id: 'expand', label: '扩写' },
	{ id: 'continue', label: '续写' },
	{ id: 'translate_en', label: '中→英' },
	{ id: 'translate_zh', label: '英→中' },
	{ id: 'extract_tags', label: '提取标签' },
	{ id: 'generate_questions', label: '生成问题' },
]

type AIAssistantPanelProps = {
	textareaRef: RefObject<HTMLTextAreaElement | null>
	content: string
	onInsert: (text: string) => void
	onReplaceSelection: (text: string) => void
	getSelectedText: () => string
}

export function AIAssistantPanel({ textareaRef, content, onInsert, onReplaceSelection, getSelectedText }: AIAssistantPanelProps) {
	const [expanded, setExpanded] = useState(false)
	const [loading, setLoading] = useState(false)
	const [result, setResult] = useState('')
	const [error, setError] = useState('')
	const abortRef = useRef<AbortController | null>(null)

	const runAction = async (action: PolishAction) => {
		const selected = getSelectedText()
		const text = selected || content

		if (!text.trim()) {
			toast.warning('请先输入内容')
			return
		}

		setLoading(true)
		setResult('')
		setError('')

		const controller = new AbortController()
		abortRef.current = controller

		let accumulated = ''

		await streamPolish(text, action, {
			onChunk: chunk => {
				accumulated += chunk
				setResult(accumulated)
			},
			onDone: () => {
				setLoading(false)
				abortRef.current = null
			},
			onError: err => {
				setError(err)
				setLoading(false)
				abortRef.current = null
			},
		}, {
			context: selected ? content : undefined,
			signal: controller.signal,
		})
	}

	const handleStop = () => {
		abortRef.current?.abort()
		setLoading(false)
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
		onInsert('\n\n' + result)
		toast.success('已插入')
	}

	const handleReplace = () => {
		onReplaceSelection(result)
		toast.success('已替换')
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
							<div className='flex items-center justify-between border-b border-white/40 p-3'>
								<span className='text-sm font-medium'>AI 助手</span>
								<button type='button' onClick={() => setExpanded(false)} className='text-gray-400 hover:text-gray-600'>
									<ChevronRight size={16} />
								</button>
							</div>

							<div className='flex flex-wrap gap-1.5 p-3'>
								{aiActions.map(a => (
									<button
										key={a.id}
										type='button'
										onClick={() => runAction(a.id)}
										disabled={loading}
										className='rounded-lg bg-white/60 px-2.5 py-1 text-xs transition-colors hover:bg-white/80 disabled:opacity-40'>
										{a.label}
									</button>
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
								<div className='flex gap-1.5 border-t border-white/40 p-3'>
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
					</motion.div>
				)}
			</AnimatePresence>

			{!expanded && (
				<button
					type='button'
					onClick={() => setExpanded(true)}
					className='ml-2 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl border border-white/40 bg-white/60 text-gray-500 backdrop-blur-sm transition-colors hover:bg-white/80 hover:text-[var(--color-brand)]'
					title='AI 助手'>
					<ChevronLeft size={16} />
				</button>
			)}
		</div>
	)
}
