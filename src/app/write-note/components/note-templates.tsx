'use client'

import { useState, useRef, useEffect, type ReactNode, type RefObject } from 'react'
import { createPortal } from 'react-dom'
import { AnimatePresence, motion } from 'motion/react'
import { BookOpen, ClipboardList, Calendar, BookMarked, FolderKanban } from 'lucide-react'
import dayjs from 'dayjs'

type NoteTemplate = {
	id: string
	label: string
	icon: ReactNode
	getContent: () => string
}

const today = () => dayjs().format('YYYY-MM-DD')

export const noteTemplates: NoteTemplate[] = [
	{
		id: 'study',
		label: '学习笔记',
		icon: <BookOpen size={14} />,
		getContent: () => `# [科目/主题]

## 核心概念

- 概念1:
- 概念2:

## 要点整理

1. 
2. 
3. 

## 例题/案例

> [!TIP]
> 

## 总结

`,
	},
	{
		id: 'meeting',
		label: '会议记录',
		icon: <ClipboardList size={14} />,
		getContent: () => `# 会议: [主题]

- **时间**: ${today()}
- **参会人**: 

## 议题

### 1. 

## 结论

- 

## 待办

- [ ] 
- [ ] 
`,
	},
	{
		id: 'diary',
		label: '日记/日志',
		icon: <Calendar size={14} />,
		getContent: () => `# ${today()} 日志

## 今日完成

- 

## 明日计划

- [ ] 

## 备注

`,
	},
	{
		id: 'reading',
		label: '读书笔记',
		icon: <BookMarked size={14} />,
		getContent: () => `# 《书名》

- **作者**: 
- **阅读日期**: ${today()}

## 核心观点

1. 

## 精彩摘录

> 

## 个人感想

`,
	},
	{
		id: 'project',
		label: '项目笔记',
		icon: <FolderKanban size={14} />,
		getContent: () => `# 项目: [名称]

## 背景


## 方案

### 方案A

### 方案B

## 当前进度

- [ ] 

## 风险与问题

> [!WARNING]
> 
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
			setPos({ top: rect.bottom + 4, left: rect.left })
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
								className='bg-card/95 fixed z-50 w-44 rounded-xl border backdrop-blur-xl'
								style={{
									top: `${pos.top}px`,
									left: `${pos.left}px`,
									boxShadow: '0 12px 40px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.2)',
								}}>
								<div className='scrollbar-none max-h-64 overflow-y-auto p-1.5'>
									{noteTemplates.map(tpl => (
										<button
											key={tpl.id}
											type='button'
											onClick={() => handleSelect(tpl)}
											className='flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-xs transition-all active:scale-[0.98] hover:bg-gray-100/50'>
											<span className='text-gray-500'>{tpl.icon}</span>
											<span>{tpl.label}</span>
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
