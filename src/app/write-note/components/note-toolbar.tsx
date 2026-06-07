'use client'

import { memo, useState, type RefObject, type ReactNode } from 'react'
import { DelayedTooltip } from '@/components/delayed-tooltip'
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
	BarChart3,
	Columns,
	Brain,
	FlipVertical,
	Palette,
} from 'lucide-react'

const COLOR_PALETTE = [
	{ name: 'red', hex: '#ef4444', label: '红色' },
	{ name: 'blue', hex: '#3b82f6', label: '蓝色' },
	{ name: 'green', hex: '#10b981', label: '绿色' },
	{ name: 'yellow', hex: '#f59e0b', label: '黄色' },
	{ name: 'purple', hex: '#8b5cf6', label: '紫色' },
	{ name: 'orange', hex: '#f97316', label: '橙色' },
	{ name: 'gray', hex: '#6b7280', label: '灰色' },
	{ name: 'pink', hex: '#ec4899', label: '粉色' },
]

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
	const [paletteOpen, setPaletteOpen] = useState(false)

	const contentBlocks = [
		{ icon: <GitBranch size={14} />, label: '流程图 (Mermaid)', template: '```mermaid\ngraph TD\n    A[开始] --> B[处理]\n    B --> C[结束]\n```' },
		{ icon: <BarChart3 size={14} />, label: '数据图表', template: '```chart\n{"type":"bar","title":"学习记录","xAxis":["周一","周二","周三"],"series":[{"name":"完成数","data":[3,5,4]}]}\n```' },
		{ icon: <Columns size={14} />, label: '对比块', template: ':::compare\ntitle: 函数与方法对比\nleft: 函数\nright: 方法\n- 定义位置：函数独立定义，方法定义在类中\n- 调用方式：函数直接调用，方法通过对象调用\n:::' },
		{ icon: <FlipVertical size={14} />, label: '复习卡片', template: '\n<details>\n<summary>问题</summary>\n\n答案内容\n\n</details>\n' },
		{ icon: <GitBranch size={14} />, label: 'Mermaid 状态图', template: '```mermaid\nstateDiagram-v2\n    [*] --> 空闲\n    空闲 --> 处理中\n    处理中 --> 完成\n    完成 --> [*]\n```' },
		{ icon: <GitBranch size={14} />, label: 'Mermaid 时间线', template: '```mermaid\ntimeline\n    title 时间线标题\n    2024 : 事件A\n         : 事件B\n    2025 : 事件C\n```' },
		{ icon: <Brain size={14} />, label: 'Markmap 知识地图', template: '```markmap\n# 中心主题\n## 分支1\n### 子项1\n### 子项2\n## 分支2\n```' },
		{ icon: <BarChart3 size={14} />, label: '图表 (ECharts)', template: '```chart\n{"type":"bar","title":"标题","xAxis":["A","B","C"],"series":[{"name":"数据","data":[10,20,15]}]}\n```' },
		{ icon: <FileCode2 size={14} />, label: '代码块 (Python)', template: '```python\npass\n```', cursorOffset: 3 },
		{ icon: <FileCode2 size={14} />, label: '代码块 (TypeScript)', template: '```typescript\n\n```', cursorOffset: 3 },
		{ icon: <Sigma size={14} />, label: '公式块', template: '$$\n\n$$', cursorOffset: 3 },
	] as { icon: ReactNode; label: string; template: string; cursorOffset?: number }[]

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
						<DelayedTooltip key={ai} content={`${action.label}${action.shortcut ? ` (${action.shortcut})` : ''}`}>
							<button
								type='button'
								onClick={() => handleClick(action)}
								aria-label={`${action.label}${action.shortcut ? `，快捷键 ${action.shortcut}` : ''}`}
								className='flex h-7 w-7 items-center justify-center rounded-md text-gray-600 transition-colors hover:bg-white/80 hover:text-gray-900'>
								{action.icon}
							</button>
						</DelayedTooltip>
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
				<DelayedTooltip content='字体颜色'>
					<button
						type='button'
						onClick={() => { setPaletteOpen(!paletteOpen); setInserterOpen(false) }}
						aria-label='字体颜色'
						className='flex h-7 w-7 items-center justify-center rounded-md text-gray-600 transition-colors hover:bg-white/80 hover:text-gray-900'>
						<Palette size={15} />
					</button>
				</DelayedTooltip>
				{paletteOpen && (
					<>
						<div className='fixed inset-0 z-10' onClick={() => setPaletteOpen(false)} />
						<div className='absolute left-0 top-full z-20 mt-1 flex gap-1.5 rounded-xl border border-white/40 bg-white/95 p-2 shadow-lg backdrop-blur-xl'>
							{COLOR_PALETTE.map(c => (
								<button
									key={c.name}
									type='button'
									onClick={() => { wrapSelection('{' + c.name + '|', '}'); setPaletteOpen(false) }}
									aria-label={c.label}
									title={c.label}
									className='h-6 w-6 rounded-full border border-white/60 transition-transform hover:scale-110'
									style={{ backgroundColor: c.hex }}
								/>
							))}
						</div>
					</>
				)}
			</div>
			<div className='mx-1 h-5 w-px bg-gray-300/50' />
			<div className='relative'>
				<DelayedTooltip content='插入内容块'>
					<button
						type='button'
						onClick={() => setInserterOpen(!inserterOpen)}
						aria-label='插入内容块'
						className='flex h-7 items-center gap-1 rounded-md px-1.5 text-gray-600 transition-colors hover:bg-white/80 hover:text-gray-900'>
						<Plus size={15} />
						<span className='text-xs'>插入</span>
					</button>
				</DelayedTooltip>
				{inserterOpen && (
					<>
						<div className='fixed inset-0 z-10' onClick={() => setInserterOpen(false)} />
						<div className='absolute left-0 top-full z-20 mt-1 w-44 rounded-xl border border-white/40 bg-white/95 p-1 shadow-lg backdrop-blur-xl'>
							{contentBlocks.map((block, i) => (
								<button
									key={i}
									type='button'
									onClick={() => { insertText('\n' + block.template + '\n'); if (block.cursorOffset !== undefined) { const ta = textareaRef.current; if (ta) { const pos = ta.selectionStart + block.cursorOffset; setTimeout(() => { ta.setSelectionRange(pos, pos); ta.focus() }, 0) } }; setInserterOpen(false) }}
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
