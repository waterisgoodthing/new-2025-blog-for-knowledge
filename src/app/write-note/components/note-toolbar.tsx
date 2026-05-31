'use client'

import { memo, type RefObject, type ReactNode } from 'react'
import {
	Bold,
	Italic,
	Strikethrough,
	Heading1,
	Heading2,
	Heading3,
	Link,
	Image,
	Table2,
	Minus,
	List,
	ListOrdered,
	ListChecks,
	Quote,
	FileCode2,
	Sigma,
	Highlighter,
} from 'lucide-react'

type ToolbarAction = {
	icon: ReactNode
	label: string
	shortcut?: string
	insert?: string
	cursorOffset?: number
	wrap?: boolean
	action?: 'insert' | 'wrap'
}

type ToolbarGroup = {
	label: string
	actions: ToolbarAction[]
}

const groups: ToolbarGroup[] = [
	{
		label: '文本格式',
		actions: [
			{ icon: <Bold size={15} />, label: '加粗', shortcut: 'Ctrl+B', wrap: true, action: 'wrap' },
			{ icon: <Italic size={15} />, label: '斜体', shortcut: 'Ctrl+I', wrap: true, action: 'wrap' },
			{ icon: <Strikethrough size={15} />, label: '删除线', insert: '~~', wrap: true, action: 'wrap' },
			{ icon: <Highlighter size={15} />, label: '高亮', insert: '==', wrap: true, action: 'wrap' },
		],
	},
	{
		label: '标题',
		actions: [
			{ icon: <Heading1 size={15} />, label: 'H1', insert: '# ', cursorOffset: 2 },
			{ icon: <Heading2 size={15} />, label: 'H2', insert: '## ', cursorOffset: 3 },
			{ icon: <Heading3 size={15} />, label: 'H3', insert: '### ', cursorOffset: 4 },
		],
	},
	{
		label: '插入',
		actions: [
			{ icon: <Link size={15} />, label: '链接', shortcut: 'Ctrl+K', insert: '[文本](url)' },
			{ icon: <Image size={15} />, label: '图片', insert: '![](url)', cursorOffset: 2 },
			{ icon: <Table2 size={15} />, label: '表格', insert: '\n| 列1 | 列2 | 列3 |\n| --- | --- | --- |\n| 内容 | 内容 | 内容 |\n' },
			{ icon: <Minus size={15} />, label: '分割线', insert: '\n---\n' },
		],
	},
	{
		label: '列表',
		actions: [
			{ icon: <List size={15} />, label: '无序列表', insert: '- ', cursorOffset: 2 },
			{ icon: <ListOrdered size={15} />, label: '有序列表', insert: '1. ', cursorOffset: 3 },
			{ icon: <ListChecks size={15} />, label: '任务', insert: '- [ ] ', cursorOffset: 6 },
			{ icon: <Quote size={15} />, label: '引用', insert: '> ', cursorOffset: 2 },
		],
	},
	{
		label: '高级',
		actions: [
			{ icon: <FileCode2 size={15} />, label: '代码块', insert: '```js\n\n```', cursorOffset: 6 },
			{ icon: <Sigma size={15} />, label: '公式块', insert: '$$\n\n$$', cursorOffset: 3 },
			{ icon: <Sigma size={15} />, label: '行内公式', insert: '$$', wrap: true, action: 'wrap' },
		],
	},
]

function WrapMap(): Record<string, { before: string; after: string }> {
	return {
		'**': { before: '**', after: '**' },
		'*': { before: '*', after: '*' },
		'~~': { before: '~~', after: '~~' },
		'==': { before: '==', after: '==' },
		'$$': { before: '$$', after: '$$' },
	}
}

type NoteToolbarProps = {
	textareaRef: RefObject<HTMLTextAreaElement | null>
	insertText: (text: string) => void
	wrapSelection: (before: string, after: string, fallback?: string) => void
	extraButtons?: ReactNode
}

export const NoteToolbar = memo(function NoteToolbar({ textareaRef, insertText, wrapSelection, extraButtons }: NoteToolbarProps) {
	const handleClick = (action: ToolbarAction) => {
		const textarea = textareaRef.current
		if (!textarea) return

		if (action.action === 'wrap' && action.insert) {
			const wrap = WrapMap()[action.insert]
			if (wrap) {
				wrapSelection(wrap.before, wrap.after)
				return
			}
		}

		if (action.action === 'wrap' && !action.insert) {
			if (action.label === '加粗') {
				wrapSelection('**', '**')
			} else if (action.label === '斜体') {
				wrapSelection('*', '*')
			}
			return
		}

		if (action.insert) {
			insertText(action.insert)
			if (action.cursorOffset !== undefined) {
				const { selectionStart } = textarea
				const newPos = selectionStart + action.cursorOffset
				setTimeout(() => {
					textarea.setSelectionRange(newPos, newPos)
					textarea.focus()
				}, 0)
			}
		}
	}

	return (
		<div className='flex flex-wrap items-center gap-0.5 rounded-lg bg-white/40 p-1.5'>
			{groups.map((group, gi) => (
				<div key={gi} className='flex items-center'>
					{gi > 0 && <div className='mx-1 h-5 w-px bg-gray-300/50' />}
					{group.actions.map((action, ai) => (
						<button
							key={ai}
							type='button'
							onClick={() => handleClick(action)}
							title={`${action.label}${action.shortcut ? ` (${action.shortcut})` : ''}`}
							className='flex h-7 w-7 items-center justify-center rounded-md text-gray-600 transition-colors hover:bg-white/80 hover:text-gray-900'>
							{action.icon}
						</button>
					))}
				</div>
			))}
			{extraButtons && (
				<>
					<div className='mx-1 h-5 w-px bg-gray-300/50' />
					{extraButtons}
				</>
			)}
		</div>
	)
})
