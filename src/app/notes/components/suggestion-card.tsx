'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { Lightbulb, Tag, FolderOpen, RefreshCw, AlertTriangle, X, Check, ChevronDown, ChevronRight } from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { getSuggestions, executeSuggestion, type Suggestion } from '@/lib/api/knowledge-assistant'

type SuggestionCardProps = {
	onRefresh?: () => void
	onExecuted?: () => void
	defaultExpanded?: boolean
}

export function SuggestionCard({ onRefresh, onExecuted, defaultExpanded = false }: SuggestionCardProps) {
	const [suggestions, setSuggestions] = useState<Suggestion[]>([])
	const [loading, setLoading] = useState(true)
	const [executing, setExecuting] = useState<string | null>(null)
	const [tagInput, setTagInput] = useState<Record<number, string>>({})
	const [expanded, setExpanded] = useState(defaultExpanded)

	useEffect(() => { setExpanded(defaultExpanded) }, [defaultExpanded])
	useEffect(() => { if (suggestions.length === 0) setExpanded(false) }, [suggestions.length])

	useEffect(() => {
		loadSuggestions()
	}, [])

	const loadSuggestions = async () => {
		setLoading(true)
		try {
			const sugs = await getSuggestions()
			setSuggestions(sugs)
		} catch {
			setSuggestions([])
		} finally {
			setLoading(false)
		}
	}

	const handleDismiss = (index: number) => {
		setSuggestions(prev => prev.filter((_, i) => i !== index))
	}

	const handleExecute = async (sug: Suggestion, index: number) => {
		if (sug.action === 'add_tag') {
			const tag = tagInput[index]?.trim()
			if (!tag) {
				toast.warning('请输入标签名')
				return
			}
			setExecuting(`${sug.action}-${index}`)
			try {
				const res = await executeSuggestion({
					type: sug.type,
					action: sug.action,
					targets: sug.targets,
					tag,
				})
				toast.success(`已为 ${res.executed} 篇内容添加标签「${tag}」`)
				handleDismiss(index)
				onExecuted?.()
			} catch (e: any) {
				toast.error('执行失败: ' + e.message)
			} finally {
				setExecuting(null)
			}
		}
	}

	if (loading) return null

	const drawerTrigger = (
		<button
			onClick={() => setExpanded(!expanded)}
			className={cn(
				'mb-6 flex w-full items-center gap-2 rounded-xl border border-white/40 bg-white/60 px-4 py-3 backdrop-blur-sm text-sm transition-colors hover:bg-white/80',
				suggestions.length === 0 ? 'text-gray-400' : 'text-[var(--color-brand)]'
			)}
			aria-label={expanded ? '收起 AI 建议' : '展开 AI 建议'}
		>
			<Lightbulb size={16} />
			<span className='flex-1 text-left'>
				{suggestions.length === 0
					? '知识库状态良好，暂无整理建议'
					: `AI 整理建议 (${suggestions.length} 条)`}
			</span>
			{expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
		</button>
	)

	if (!expanded) return drawerTrigger

	if (suggestions.length === 0) {
		return drawerTrigger
	}

	const typeIcons: Record<string, React.ReactNode> = {
		tag: <Tag size={14} />,
		folder: <FolderOpen size={14} />,
		review: <AlertTriangle size={14} />,
		summary: <Lightbulb size={14} />,
		activity: <Lightbulb size={14} />,
	}

	const typeColors: Record<string, string> = {
		tag: 'border-blue-200/70 bg-blue-50/50',
		folder: 'border-amber-200/70 bg-amber-50/50',
		review: 'border-red-200/70 bg-red-50/50',
		summary: 'border-green-200/70 bg-green-50/50',
		activity: 'border-green-200/70 bg-green-50/50',
	}

	const isActionable = (action: string) => ['add_tag', 'move_to_folder'].includes(action)

	return (
		<div className='mb-6 rounded-xl border border-white/40 bg-white/60 p-4 backdrop-blur-sm'>
			<div className='mb-3 flex items-center justify-between'>
				<div className='flex items-center gap-2'>
					<Lightbulb size={16} className='text-[var(--color-brand)]' />
					<h3 className='text-sm font-semibold text-gray-800'>AI 整理建议</h3>
				</div>
				<div className='flex items-center gap-1'>
					<button
						onClick={() => { loadSuggestions(); onRefresh?.() }}
						className='text-gray-400 hover:text-gray-600'
						aria-label='刷新建议'
					>
						<RefreshCw size={14} />
					</button>
					<button
						onClick={() => setExpanded(false)}
						className='text-gray-400 hover:text-gray-600'
						aria-label='收起 AI 建议'
					>
						<ChevronDown size={14} />
					</button>
				</div>
			</div>

			<div className='space-y-2'>
				{suggestions.slice(0, 4).map((sug, i) => (
					<motion.div
						key={`${sug.type}-${sug.action}-${i}`}
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: i * 0.05 }}
						className={cn('rounded-lg border p-3', typeColors[sug.type] || 'border-gray-200/70 bg-gray-50/50')}
					>
						<div className='flex items-start gap-2.5'>
							<span className='mt-0.5 shrink-0 text-gray-500'>{typeIcons[sug.type] || <Lightbulb size={14} />}</span>
							<div className='min-w-0 flex-1'>
								<div className='text-xs font-medium text-gray-700'>{sug.title}</div>
								<div className='mt-0.5 text-[11px] leading-4 text-gray-500'>{sug.description}</div>
								{sug.targets.length > 0 && (
									<div className='mt-1 text-[10px] text-gray-400'>影响 {sug.targets.length} 项</div>
								)}
							</div>
							<button
								onClick={() => handleDismiss(i)}
								className='shrink-0 text-gray-300 hover:text-gray-500'
								aria-label='忽略'
							>
								<X size={12} />
							</button>
						</div>

						{sug.action === 'add_tag' && (
							<div className='mt-2 flex items-center gap-2'>
								<input
									value={tagInput[i] || ''}
									onChange={e => setTagInput(prev => ({ ...prev, [i]: e.target.value }))}
									placeholder='输入标签名'
									className='flex-1 rounded-md border border-white/40 bg-white/60 px-2 py-1 text-[11px] outline-none focus:border-[var(--color-brand)]'
									onKeyDown={e => e.key === 'Enter' && handleExecute(sug, i)}
								/>
								<button
									onClick={() => handleExecute(sug, i)}
									disabled={executing === `add_tag-${i}`}
									className='flex items-center gap-1 rounded-md bg-[var(--color-brand)]/10 px-2 py-1 text-[11px] text-[var(--color-brand)] hover:bg-[var(--color-brand)]/20 disabled:opacity-50'
								>
									<Check size={10} />
									执行
								</button>
							</div>
						)}

						{sug.action === 'move_to_folder' && (
							<div className='mt-2 flex items-center gap-2'>
								<span className='text-[11px] text-gray-400'>{sug.targets.length} 篇未归档</span>
							</div>
						)}
					</motion.div>
				))}
			</div>
		</div>
	)
}
