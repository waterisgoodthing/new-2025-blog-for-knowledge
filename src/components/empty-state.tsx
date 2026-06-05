'use client'

import { type ReactNode } from 'react'
import { FileText, Search, LogIn, AlertTriangle } from 'lucide-react'
import Link from 'next/link'

type EmptyStateVariant = 'no-content' | 'no-results' | 'not-logged-in' | 'load-error'

type EmptyStateProps = {
	variant: EmptyStateVariant
	title?: string
	description?: string
	action?: { label: string; href?: string; onClick?: () => void }
	icon?: ReactNode
}

const defaults: Record<EmptyStateVariant, { icon: ReactNode; title: string; description: string; action?: { label: string; href: string } }> = {
	'no-content': {
		icon: <FileText className='h-10 w-10' />,
		title: '还没有内容',
		description: '创建你的第一篇笔记开始记录吧',
		action: { label: '新建笔记', href: '/write-note' },
	},
	'no-results': {
		icon: <Search className='h-10 w-10' />,
		title: '没有匹配结果',
		description: '试试调整筛选条件或关键词',
	},
	'not-logged-in': {
		icon: <LogIn className='h-10 w-10' />,
		title: '需要登录',
		description: '登录后查看和管理你的内容',
	},
	'load-error': {
		icon: <AlertTriangle className='h-10 w-10' />,
		title: '加载失败',
		description: '网络异常或服务暂时不可用',
	},
}

export function EmptyState({ variant, title, description, action, icon }: EmptyStateProps) {
	const d = defaults[variant]
	const finalTitle = title ?? d.title
	const finalDesc = description ?? d.description
	const finalIcon = icon ?? d.icon
	const finalAction = action ?? d.action

	return (
		<div className='flex flex-col items-center justify-center rounded-xl border border-white/40 bg-white/60 px-6 py-16 text-center backdrop-blur-sm'>
			<div className='mb-3 text-gray-300'>{finalIcon}</div>
			<h3 className='mb-1 text-sm font-medium text-gray-600'>{finalTitle}</h3>
			<p className='mb-4 text-xs text-gray-400'>{finalDesc}</p>
			{finalAction && (
				'href' in finalAction && finalAction.href ? (
					<Link
						href={finalAction.href}
						className='rounded-lg bg-[var(--color-brand)]/10 px-4 py-2 text-xs font-medium text-[var(--color-brand)] transition-colors hover:bg-[var(--color-brand)]/20'
					>
						{finalAction.label}
					</Link>
				) : 'onClick' in finalAction && finalAction.onClick ? (
					<button
						type='button'
						onClick={finalAction.onClick}
						className='rounded-lg bg-[var(--color-brand)]/10 px-4 py-2 text-xs font-medium text-[var(--color-brand)] transition-colors hover:bg-[var(--color-brand)]/20'
					>
						{finalAction.label}
					</button>
				) : null
			)}
		</div>
	)
}
