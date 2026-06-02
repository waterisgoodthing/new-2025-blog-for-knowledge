'use client'

import { useState, useRef, useEffect, type ReactNode, type RefObject } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, motion } from 'motion/react'
import { BookOpen, ClipboardCheck, BookMarked, FolderKanban } from 'lucide-react'
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
		id: 'class-note',
		label: '课堂笔记',
		description: '整理课堂概念、例题、疑问和课后复盘。',
		icon: <BookOpen size={14} />,
		getContent: () => `# [课程/主题]

- **日期**: ${today()}
- **科目**:

## 课堂目标

-

## 核心概念

- 概念:
- 作用:
- 易混点:

## 例题

- 题目:
- 解法:
- 关键步骤:

## 我的疑问

-

## 课后复盘

- 今天真正掌握的是:
- 需要回看的是:
`,
	},
	{
		id: 'mistake-analysis',
		label: '错题解析',
		description: '拆解题目、错误原因、正确思路和复习建议。',
		icon: <ClipboardCheck size={14} />,
		getContent: () => `# 错题: [题目关键词]

- **日期**: ${today()}
- **科目**:
- **难度**: 中等

## 题目


## 我的答案


## 正确答案


## 错因分析

- 我卡住的位置:
- 错误原因:
- 易混陷阱:

## 知识点

-

## 复习安排

- 今天:
- 3 天后:
- 7 天后:
`,
	},
	{
		id: 'reading',
		label: '读书笔记',
		description: '记录书籍观点、摘录、自己的理解和可迁移结论。',
		icon: <BookMarked size={14} />,
		getContent: () => `# 《书名》

- **作者**: 
- **阅读日期**: ${today()}

## 核心观点

1. 

## 关键摘录

> 

## 我的理解


## 可迁移结论

`,
	},
	{
		id: 'project-review',
		label: '项目复盘',
		description: '复盘目标、决策、结果、风险和下一步动作。',
		icon: <FolderKanban size={14} />,
		getContent: () => `# 项目复盘: [名称]

- **日期**: ${today()}

## 背景


## 目标


## 过程记录

- 做了什么:
- 关键决策:
- 遇到的问题:

## 结果


## 经验

- 继续保留:
- 下次改进:

## 下一步

- [ ]
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
			<button
				ref={btnRef}
				type='button'
				onClick={() => setOpen(!open)}
				aria-label='打开笔记模板面板'
				aria-haspopup='menu'
				aria-expanded={open}
				title='插入模板'
				className='flex h-7 items-center gap-1 rounded-md px-2 text-xs text-gray-600 transition-colors hover:bg-white/80 hover:text-gray-900'>
				<FolderKanban size={14} />
				<span>模板</span>
			</button>

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
