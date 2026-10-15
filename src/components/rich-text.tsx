'use client'

import { useMarkdownRender } from '@/hooks/use-markdown-render'
import { cn } from '@/lib/utils'

interface RichTextProps {
	content: string | null | undefined
	className?: string
	fallback?: string | null
}

export function RichText({ content, className, fallback }: RichTextProps) {
	const text = content || fallback || ''
	const { content: rendered, loading } = useMarkdownRender(text)

	if (!text) return null

	if (loading) {
		return <div className={cn('animate-pulse bg-gray-100 rounded h-16', className)} />
	}

	return (
		<div className={cn('prose prose-sm max-w-none break-words', className)}>
			{rendered || <div className='whitespace-pre-wrap'>{text}</div>}
		</div>
	)
}
