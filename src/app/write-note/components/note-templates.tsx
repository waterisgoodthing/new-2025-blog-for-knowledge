'use client'

import { useState, useRef, useEffect, type ReactNode, type RefObject } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, motion } from 'motion/react'
import { BookOpen, Lightbulb, FileSearch, RotateCcw, ListTodo, Layers, PencilLine, FolderKanban } from 'lucide-react'
import { DelayedTooltip } from '@/components/delayed-tooltip'
import dayjs from 'dayjs'

type NoteTemplate = {
	id: string
	label: string
	description: string
	icon: ReactNode
	getContent: () => string
}

const today = () => dayjs().format('YYYY-MM-DD')

export const noteTemplates: NoteTemplate[] = [
	{
		id: 'capture',
		label: '记录型',
		description: '记录事实、来源、上下文和原始观察。',
		icon: <BookOpen size={14} />,
		getContent: () => `# 记录: [主题]

- **日期**: ${today()}
- **来源**:

## 事实

-

## 上下文

-

## 原始观察

-

## 疑问

-
`,
	},
	{
		id: 'understand',
		label: '理解型',
		description: '解释概念、关系、举例和开放问题。',
		icon: <Lightbulb size={14} />,
		getContent: () => `# 理解: [概念/主题]

- **日期**: ${today()}

## 概念定义

-

## 关键关系

-

## 举例说明

-

## 容易混淆的点

-

## 开放问题

-
`,
	},
	{
		id: 'analyze',
		label: '分析型',
		description: '拆解问题、原因、证据、备选和结论。',
		icon: <FileSearch size={14} />,
		getContent: () => `# 分析: [问题/主题]

- **日期**: ${today()}

## 问题

-

## 原因分析

-

## 证据

-

## 备选方案

-

## 结论

-
`,
	},
	{
		id: 'review',
		label: '复盘型',
		description: '对比目标/过程/结果，提炼经验和下一步动作。',
		icon: <RotateCcw size={14} />,
		getContent: () => `# 复盘: [事项]

- **日期**: ${today()}

## 目标

-

## 过程记录

-

## 结果

-

## 经验教训

- 继续保留:
- 下次改进:

## 下一步

- [ ]
`,
	},
	{
		id: 'plan',
		label: '计划型',
		description: '定义目标、约束、任务、优先级和检查节点。',
		icon: <ListTodo size={14} />,
		getContent: () => `# 计划: [目标]

- **日期**: ${today()}

## 目标

-

## 约束条件

-

## 任务拆解

- [ ] 任务1
- [ ] 任务2
- [ ] 任务3

## 优先级

1.
2.
3.

## 检查节点

-
`,
	},
	{
		id: 'organize',
		label: '整理型',
		description: '将杂乱笔记整理为大纲、表格、清单或知识图谱。',
		icon: <Layers size={14} />,
		getContent: () => `# 整理: [主题]

- **日期**: ${today()}

## 原始信息

### A

### B

## 共性提炼

-

## 分类

1.
2.

## 结构化结论

-
`,
	},
	{
		id: 'express',
		label: '表达型',
		description: '将内容整理为文章、说明、总结或演示提纲。',
		icon: <PencilLine size={14} />,
		getContent: () => `# 表达: [主题]

- **日期**: ${today()}

## 核心观点

-

## 论证支撑

-

## 案例/举例

-

## 总结

-

## 待补充

-
`,
	},
]

type NoteTemplatesDropdownProps = {
	onInsert: (text: string) => void
	textareaRef?: RefObject<HTMLTextAreaElement | null>
}

export function NoteTemplatesDropdown({ onInsert, textareaRef }: NoteTemplatesDropdownProps) {
	const [open, setOpen] = useState(false)
	const [mounted, setMounted] = useState(false)
	const btnRef = useRef<HTMLButtonElement>(null)
	const dropdownRef = useRef<HTMLDivElement>(null)
	const [pos, setPos] = useState({ top: 0, left: 0 })

	useEffect(() => {
		setMounted(true)
	}, [])

	useEffect(() => {
		if (open && btnRef.current) {
			const rect = btnRef.current.getBoundingClientRect()
			const menuWidth = 288
			const viewportPadding = 8
			const maxLeft = Math.max(viewportPadding, window.innerWidth - menuWidth - viewportPadding)
			setPos({ top: rect.bottom + 4, left: Math.min(Math.max(viewportPadding, rect.left), maxLeft) })
		}
	}, [open])

	useEffect(() => {
		if (!open) return
		const handleClick = (e: MouseEvent) => {
			const t = e.target as Node
			if (btnRef.current?.contains(t) || dropdownRef.current?.contains(t)) return
			setOpen(false)
		}
		const handleEsc = (e: KeyboardEvent) => {
			if (e.key === 'Escape') setOpen(false)
		}
		document.addEventListener('mousedown', handleClick)
		document.addEventListener('keydown', handleEsc)
		return () => {
			document.removeEventListener('mousedown', handleClick)
			document.removeEventListener('keydown', handleEsc)
		}
	}, [open])

	const handleSelect = (tpl: NoteTemplate) => {
		let text = tpl.getContent()
		const textarea = textareaRef?.current
		if (textarea) {
			const { selectionStart, selectionEnd, value } = textarea
			const charBefore = selectionStart > 0 ? value[selectionStart - 1] : ''
			const charAfter = selectionEnd < value.length ? value[selectionEnd] : ''
			if (charBefore && !/\s/.test(charBefore)) {
				text = '\n\n' + text
			}
			if (charAfter && !/\s/.test(charAfter)) {
				text = text + '\n\n'
			}
		}
		onInsert(text)
		setOpen(false)
	}

	return (
		<>
			<DelayedTooltip content='插入模板到光标位置'>
				<button
					ref={btnRef}
					type='button'
					onClick={() => setOpen(!open)}
					aria-label='打开笔记模板面板'
					aria-haspopup='menu'
					aria-expanded={open}
					className='flex h-7 items-center gap-1 rounded-md px-2 text-xs text-gray-600 transition-colors hover:bg-white/80 hover:text-gray-900'>
					<FolderKanban size={14} />
					<span>模板</span>
				</button>
			</DelayedTooltip>

			{mounted &&
				createPortal(
					<AnimatePresence>
						{open && (
							<motion.div
								ref={dropdownRef}
								initial={{ opacity: 0, y: -8, scale: 0.95 }}
								animate={{ opacity: 1, y: 0, scale: 1 }}
								exit={{ opacity: 0, y: -8, scale: 0.95 }}
								transition={{ duration: 0.15 }}
								role='menu'
								aria-label='笔记模板'
								className='bg-card/95 fixed z-50 w-72 rounded-xl border backdrop-blur-xl'
								style={{
									top: `${pos.top}px`,
									left: `${pos.left}px`,
									boxShadow: '0 12px 40px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.2)',
								}}>
								<div className='scrollbar-none max-h-80 overflow-y-auto p-2'>
									{noteTemplates.map(tpl => (
										<button
											key={tpl.id}
											type='button'
											onClick={() => handleSelect(tpl)}
											role='menuitem'
											className='flex w-full items-start gap-3 rounded-lg px-3 py-2.5 text-left text-xs transition-all active:scale-[0.98] hover:bg-gray-100/50'>
											<span className='mt-0.5 text-gray-500'>{tpl.icon}</span>
											<span className='min-w-0'>
												<span className='block font-medium text-gray-800'>{tpl.label}</span>
												<span className='mt-0.5 block leading-4 text-gray-500'>{tpl.description}</span>
											</span>
										</button>
									))}
								</div>
							</motion.div>
						)}
					</AnimatePresence>,
					document.body
				)}
		</>
	)
}
