import React, { useEffect, useRef, useState } from 'react'

import { drawIsolatedChart } from '../chart'
import { renderMarkdownPoC } from '../render-poc'

export type PoCBrowserSurfaceProps = {
	markdown: string
	mode: 'public' | 'admin-preview'
}

export function PoCBrowserSurface({ markdown, mode }: PoCBrowserSurfaceProps) {
	const result = renderMarkdownPoC(markdown, { mode })
	const contentRef = useRef<HTMLDivElement>(null)
	const [phase, setPhase] = useState('ssr')

	useEffect(() => {
		setPhase('hydrated')
	}, [])

	useEffect(() => {
		for (const canvas of contentRef.current?.querySelectorAll<HTMLCanvasElement>('canvas[data-poc-chart-source]') ?? []) {
			const source = canvas.dataset.pocChartSource
			if (source) drawIsolatedChart(canvas, source)
		}
	}, [markdown, phase])

	return React.createElement(
		'div',
		{
			'data-outcome': result.outcome,
			'data-poc-phase': phase,
			'data-warning-count': result.warnings.length
		},
		React.createElement('div', {
			ref: contentRef,
			className: 'poc-content',
			dangerouslySetInnerHTML: { __html: result.html }
		}),
		React.createElement(
			'ul',
			{ className: 'poc-toc' },
			...result.toc.map(item => React.createElement('li', { key: item.id, 'data-level': item.level }, item.text))
		),
		React.createElement(
			'ul',
			{ className: 'poc-warnings' },
			...result.warnings.map(warning => React.createElement('li', { key: warning.code, 'data-code': warning.code }, warning.message))
		)
	)
}
