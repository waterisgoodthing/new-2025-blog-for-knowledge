'use client'

import { memo } from 'react'
import { useMarkdownRender } from '@/hooks/use-markdown-render'

export const NotePreviewContent = memo(function NotePreviewContent({ content }: { content: string }) {
	const { content: rendered, loading } = useMarkdownRender(content)

	if (loading) return <div className='py-10 text-center text-gray-400'>渲染中...</div>

	return <div className='prose prose-sm max-w-none min-h-[400px] rounded-xl border border-white/40 bg-white/60 p-6'>{rendered}</div>
})
