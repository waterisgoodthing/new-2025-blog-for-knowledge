'use client'

import { useState, useEffect, useRef, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, motion } from 'motion/react'
import {
	Heading1,
	Heading2,
	Heading3,
	FileCode2,
	Sigma,
	Table2,
	ListChecks,
	Quote,
	AlertCircle,
	AlertTriangle,
	Minus,
	Clock,
} from 'lucide-react'
import type { SlashState } from '../hooks/use-note-editor'

type SlashCommand = {
	id: string
	label: string
	description: string
	icon: ReactNode
	insert: string
	cursorOffset?: number
}

const slashCommands: SlashCommand[] = [
	{ id: 'h1', label: '标题1', description: '一级标题', icon: <Heading1 size={14} />, insert: '# ', cursorOffset: 2 },
	{ id: 'h2', label: '标题2', description: '二级标题', icon: <Heading2 size={14} />, insert: '## ', cursorOffset: 3 },
	{ id: 'h3', label: '标题3', description: '三级标题', icon: <Heading3 size={14} />, insert: '### ', cursorOffset: 4 },
	{ id: 'code', label: '代码块', description: '插入代码块', icon: <FileCode2 size={14} />, insert: '```js\n\n```', cursorOffset: 6 },
	{ id: 'math', label: '公式', description: '公式块', icon: <Sigma size={14} />, insert: '$$\n\n$$', cursorOffset: 3 },
	{ id: 'table', label: '表格', description: '插入表格', icon: <Table2 size={14} />, insert: '\n| 列1 | 列2 | 列3 |\n| --- | --- | --- |\n| 内容 | 内容 | 内容 |\n' },
	{ id: 'task', label: '任务', description: '任务列表项', icon: <ListChecks size={14} />, insert: '- [ ] ', cursorOffset: 6 },
	{ id: 'quote', label: '引用', description: '引用块', icon: <Quote size={14} />, insert: '> ', cursorOffset: 2 },
	{ id: 'note', label: '提示', description: 'NOTE 提示框', icon: <AlertCircle size={14} />, insert: '> [!NOTE]\n> ' },
	{ id: 'warning', label: '警告', description: 'WARNING 提示框', icon: <AlertTriangle size={14} />, insert: '> [!WARNING]\n> ' },
	{ id: 'hr', label: '分割线', description: '水平分割线', icon: <Minus size={14} />, insert: '\n---\n' },
	{ id: 'time', label: '时间戳', description: '当前日期时间', icon: <Clock size={14} />, insert: '' },
]

function filterCommands(query: string): SlashCommand[] {
	if (!query) return slashCommands
	const q = query.toLowerCase()
	return slashCommands.filter(
		cmd => cmd.label.toLowerCase().includes(q) || cmd.description.toLowerCase().includes(q)
	)
}

type SlashCommandMenuProps = {
	slashState: SlashState
	onClose: () => void
	onSelect: (insert: string) => void
}

export function SlashCommandMenu({ slashState, onClose, onSelect }: SlashCommandMenuProps) {
	const [selectedIdx, setSelectedIdx] = useState(0)
	const [mounted, setMounted] = useState(false)
	const listRef = useRef<HTMLDivElement>(null)
	const itemRefs = useRef<(HTMLButtonElement | null)[]>([])

	const filtered = filterCommands(slashState.query)

	useEffect(() => {
		setMounted(true)
	}, [])

	useEffect(() => {
		setSelectedIdx(0)
	}, [slashState.query])

	useEffect(() => {
		if (!slashState.open) return

		const handleKeyDown = (e: KeyboardEvent) => {
			if (e.key === 'ArrowDown') {
				e.preventDefault()
				setSelectedIdx(i => Math.min(i + 1, filtered.length - 1))
			} else if (e.key === 'ArrowUp') {
				e.preventDefault()
				setSelectedIdx(i => Math.max(i - 1, 0))
			} else if (e.key === 'Enter') {
				e.preventDefault()
				const cmd = filtered[selectedIdx]
				if (cmd) {
					const text = cmd.id === 'time'
						? new Date().toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).replace(/\//g, '-')
						: cmd.insert
					onSelect(text)
				}
				onClose()
			} else if (e.key === 'Escape') {
				e.preventDefault()
				onClose()
			}
		}

		window.addEventListener('keydown', handleKeyDown, true)
		return () => window.removeEventListener('keydown', handleKeyDown, true)
	}, [slashState.open, filtered, selectedIdx, onClose, onSelect])

	useEffect(() => {
		itemRefs.current[selectedIdx]?.scrollIntoView({ block: 'nearest' })
	}, [selectedIdx])

	if (!slashState.open || filtered.length === 0) return null

	const handleSelect = (cmd: SlashCommand) => {
		const text = cmd.id === 'time'
			? new Date().toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).replace(/\//g, '-')
			: cmd.insert
		onSelect(text)
		onClose()
	}

	return mounted
		? createPortal(
				<AnimatePresence>
					<motion.div
						initial={{ opacity: 0, y: -8, scale: 0.95 }}
						animate={{ opacity: 1, y: 0, scale: 1 }}
						exit={{ opacity: 0, y: -8, scale: 0.95 }}
						transition={{ duration: 0.12 }}
						className='bg-card/95 fixed z-50 w-56 rounded-xl border backdrop-blur-xl'
						style={{
							top: `${slashState.position.top}px`,
							left: `${slashState.position.left}px`,
							boxShadow: '0 12px 40px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.2)',
						}}>
						<div ref={listRef} className='scrollbar-none max-h-64 overflow-y-auto p-1.5'>
							{filtered.map((cmd, i) => (
								<button
									key={cmd.id}
									ref={el => { itemRefs.current[i] = el }}
									type='button'
									onMouseDown={e => { e.preventDefault(); handleSelect(cmd) }}
									onMouseEnter={() => setSelectedIdx(i)}
									className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-xs transition-all ${
										i === selectedIdx ? 'bg-brand/10 text-brand font-medium' : 'hover:bg-gray-100/50'
									}`}>
									<span className='flex-shrink-0 text-gray-500'>{cmd.icon}</span>
									<div className='flex-1 min-w-0'>
										<div>{cmd.label}</div>
										<div className='text-[10px] text-gray-400 truncate'>{cmd.description}</div>
									</div>
								</button>
							))}
						</div>
					</motion.div>
				</AnimatePresence>,
				document.body
		  )
		: null
}
