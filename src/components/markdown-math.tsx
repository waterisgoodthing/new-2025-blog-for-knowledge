'use client'

import { useMemo } from 'react'
import katex from 'katex'

interface MarkdownMathProps {
	content: string
	displayMode: boolean
	tag: 'div' | 'span'
}

export function MarkdownMath({ content, displayMode, tag }: MarkdownMathProps) {
	const html = useMemo(() => {
		try {
			return katex.renderToString(content, {
				displayMode,
				throwOnError: false,
				output: 'html',
				strict: 'ignore',
			})
		} catch {
			return displayMode ? `$$${content}$$` : `$${content}$`
		}
	}, [content, displayMode])

	const Tag = tag
	return <Tag className='ag-math' dangerouslySetInnerHTML={{ __html: html }} />
}
