'use client'

import { memo, useState, type RefObject, type ReactNode } from 'react'
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
	Plus,
	GitBranch,
	Columns,
	Brain,
	FlipVertical,
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
	const [inserterOpen, setInserterOpen] = useState(false)

	const contentBlocks = [
		{ icon: <GitBranch size={14} />, label: '图表 (Mermaid)', template: '```mermaid\ngraph TD\n    A[开始] --> B[处理]\n    B --> C[结束]\n```' },
		{ icon: <Columns size={14} />, label: '对比块', template: ':::compare\ntitle: 对比标题\nleft: 选项A\nright: 选项B\n- 区别1\n- 区别2\n:::' },
		{ icon: <Brain size={14} />, label: '思维导图', template: '```mermaid\nmindmap\n  root((中心主题))\n    分支1\n      子项1\n      子项2\n    分支2\n```' },
		{ icon: <FlipVertical size={14} />, label: '复习卡片', template: '\n<details>\n<summary>问题</summary>\n\n答案内容\n\n</details>\n' },
	]

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
							aria-label={`${action.label}${action.shortcut ? `，快捷键 ${action.shortcut}` : ''}`}
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
			<div className='mx-1 h-5 w-px bg-gray-300/50' />
			<div className='relative'>
				<button
					type='button'
					onClick={() => setInserterOpen(!inserterOpen)}
					aria-label='插入内容块'
					title='插入内容块'
					className='flex h-7 items-center gap-1 rounded-md px-1.5 text-gray-600 transition-colors hover:bg-white/80 hover:text-gray-900'>
					<Plus size={15} />
					<span className='text-xs'>插入</span>
				</button>
				{inserterOpen && (
					<>
						<div className='fixed inset-0 z-10' onClick={() => setInserterOpen(false)} />
						<div className='absolute left-0 top-full z-20 mt-1 w-44 rounded-xl border border-white/40 bg-white/95 p-1 shadow-lg backdrop-blur-xl'>
							{contentBlocks.map((block, i) => (
								<button
									key={i}
									type='button'
									onClick={() => { insertText('\n' + block.template + '\n'); setInserterOpen(false) }}
									className='flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-xs transition-colors hover:bg-gray-100/50'>
									{block.icon}
									<span>{block.label}</span>
								</button>
							))}
						</div>
					</>
				)}
			</div>
		</div>
	)
})
