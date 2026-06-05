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
	Bold,
	Italic,
	Highlighter,
	FoldVertical,
	GitBranch,
	Map,
	ListOrdered,
} from 'lucide-react'
import type { SlashState } from '../hooks/use-note-editor'

type SlashCommand = {
	id: string
	label: string
	aliases: string[]
	description: string
	icon: ReactNode
	insert: string
	cursorOffset?: number
}

const slashCommands: SlashCommand[] = [
	{ id: 'h1', label: '标题1', aliases: ['bt1', 'heading1', 'title1'], description: '一级标题', icon: <Heading1 size={14} />, insert: '# ', cursorOffset: 2 },
	{ id: 'h2', label: '标题2', aliases: ['bt2', 'heading2', 'title2'], description: '二级标题', icon: <Heading2 size={14} />, insert: '## ', cursorOffset: 3 },
	{ id: 'h3', label: '标题3', aliases: ['bt3', 'heading3', 'title3'], description: '三级标题', icon: <Heading3 size={14} />, insert: '### ', cursorOffset: 4 },
	{ id: 'bold', label: '加粗', aliases: ['jb', 'bold'], description: '加粗文本', icon: <Bold size={14} />, insert: '****', cursorOffset: 2 },
	{ id: 'italic', label: '斜体', aliases: ['xt', 'italic'], description: '斜体文本', icon: <Italic size={14} />, insert: '**', cursorOffset: 1 },
	{ id: 'highlight', label: '高亮', aliases: ['gl', 'highlight'], description: '高亮文本', icon: <Highlighter size={14} />, insert: '====', cursorOffset: 2 },
	{ id: 'code', label: '代码块', aliases: ['dmk', 'code', 'codeblock'], description: '插入代码块', icon: <FileCode2 size={14} />, insert: '```js\n\n```', cursorOffset: 6 },
	{ id: 'math', label: '公式', aliases: ['gs', 'math'], description: '公式块', icon: <Sigma size={14} />, insert: '$$\n\n$$', cursorOffset: 3 },
	{ id: 'math-inline', label: '行内公式', aliases: ['hngs', 'inline-math'], description: '行内公式', icon: <Sigma size={14} />, insert: '$$', cursorOffset: 1 },
	{ id: 'table', label: '表格', aliases: ['bg', 'table'], description: '插入表格', icon: <Table2 size={14} />, insert: '\n| 列1 | 列2 | 列3 |\n| --- | --- | --- |\n| 内容 | 内容 | 内容 |\n' },
	{ id: 'task', label: '任务', aliases: ['rw', 'task', 'todo', 'checkbox'], description: '任务列表项', icon: <ListChecks size={14} />, insert: '- [ ] ', cursorOffset: 6 },
	{ id: 'olist', label: '有序列表', aliases: ['yxlb', 'ordered'], description: '有序列表', icon: <ListOrdered size={14} />, insert: '1. ', cursorOffset: 3 },
	{ id: 'quote', label: '引用', aliases: ['yy', 'quote', 'blockquote'], description: '引用块', icon: <Quote size={14} />, insert: '> ', cursorOffset: 2 },
	{ id: 'note', label: '提示', aliases: ['ts', 'note', 'info'], description: 'NOTE 提示框', icon: <AlertCircle size={14} />, insert: '> [!NOTE]\n> ' },
	{ id: 'tip', label: '技巧', aliases: ['jq', 'tip'], description: 'TIP 提示框', icon: <AlertCircle size={14} />, insert: '> [!TIP]\n> ' },
	{ id: 'warning', label: '警告', aliases: ['jg', 'warning', 'warn'], description: 'WARNING 提示框', icon: <AlertTriangle size={14} />, insert: '> [!WARNING]\n> ' },
	{ id: 'caution', label: '危险', aliases: ['wx', 'caution'], description: 'CAUTION 提示框', icon: <AlertTriangle size={14} />, insert: '> [!CAUTION]\n> ' },
	{ id: 'important', label: '重要', aliases: ['zy', 'important'], description: 'IMPORTANT 提示框', icon: <AlertCircle size={14} />, insert: '> [!IMPORTANT]\n> ' },
	{ id: 'hr', label: '分割线', aliases: ['fgx', 'hr', 'divider'], description: '水平分割线', icon: <Minus size={14} />, insert: '\n---\n' },
	{ id: 'time', label: '时间戳', aliases: ['sjb', 'time', 'timestamp', 'date'], description: '当前日期时间', icon: <Clock size={14} />, insert: '' },
	{ id: 'details', label: '折叠', aliases: ['zd', 'details', 'fold', 'collapse'], description: '可折叠区域', icon: <FoldVertical size={14} />, insert: '<details>\n<summary>标题</summary>\n\n内容\n</details>' },
	{ id: 'mermaid', label: '图表', aliases: ['tb', 'mermaid', 'flowchart', 'flow'], description: 'Mermaid 流程图', icon: <GitBranch size={14} />, insert: '```mermaid\ngraph TD\nA-->B\n```' },
	{ id: 'mindmap', label: '思维导图', aliases: ['swdt', 'mindmap', 'mind'], description: 'Markmap 思维导图', icon: <Map size={14} />, insert: '```markmap\n# 主题\n## 分支1\n### 子项\n## 分支2\n```' },
	{ id: 'chart', label: '数据图表', aliases: ['tbzt', 'chart', 'echarts'], description: 'ECharts 数据图表', icon: <GitBranch size={14} />, insert: '```chart\n{"type":"bar","title":"图表标题","xAxis":["A","B","C"],"series":[{"name":"数据","data":[10,20,15]}]}\n```' },
	{ id: 'footnote', label: '脚注', aliases: ['jz', 'footnote', 'fn'], description: '脚注引用', icon: <Sigma size={14} />, insert: '[^1]', cursorOffset: 3 },
]

function filterCommands(query: string): SlashCommand[] {
	if (!query) return slashCommands
	const q = query.toLowerCase()
	return slashCommands.filter(cmd =>
		cmd.label.toLowerCase().includes(q) ||
		cmd.description.toLowerCase().includes(q) ||
		cmd.aliases.some(alias => alias.toLowerCase().includes(q))
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
	const menuRef = useRef<HTMLDivElement>(null)
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

		const handleOutsideClick = (e: MouseEvent) => {
			if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
				onClose()
			}
		}
		document.addEventListener('mousedown', handleOutsideClick)
		return () => document.removeEventListener('mousedown', handleOutsideClick)
	}, [slashState.open, onClose])

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
						ref={menuRef}
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
