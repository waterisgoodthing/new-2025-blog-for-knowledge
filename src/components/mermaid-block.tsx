'use client'

import { useEffect, useRef, useState } from 'react'
import { DiagramViewer } from '@/components/diagram-viewer'

let mermaidPromise: Promise<any> | null = null
let mermaidFailed = false

async function getMermaid(): Promise<any> {
	if (mermaidFailed) throw new Error('mermaid not available')
	if (!mermaidPromise) {
		mermaidPromise = (async () => {
			try {
				const mod = await import('mermaid')
				const m = mod.default ?? mod
				m.initialize({
					startOnLoad: false,
					theme: 'default',
					securityLevel: 'strict',
					logLevel: 0,
				})
				return m
			} catch (err) {
				console.warn('Failed to load mermaid:', err)
				mermaidFailed = true
				mermaidPromise = null
				throw err
			}
		})()
	}
	return mermaidPromise
}

function isLikelyMermaid(code: string): boolean {
	if (!code || code.trim().length < 3) return false
	const trimmed = code.trim()
	const prefixes = [
		'graph ', 'flowchart ', 'sequenceDiagram', 'classDiagram',
		'stateDiagram', 'erDiagram', 'gantt', 'pie', 'timeline',
		'journey', 'quadrantChart', 'requirementDiagram', 'gitgraph',
		'block-beta', 'mindmap', 'sankey', 'xychart',
	]
	return prefixes.some(p => trimmed.startsWith(p))
}

export function MermaidBlock({ code }: { code: string }) {
	const containerRef = useRef<HTMLDivElement>(null)
	const [svg, setSvg] = useState('')
	const [error, setError] = useState(false)

	useEffect(() => {
		let cancelled = false

		async function render() {
			if (!isLikelyMermaid(code)) {
				if (!cancelled) setError(true)
				return
			}

			try {
				const mermaid = await getMermaid()
				const id = `mermaid-${Math.random().toString(36).slice(2, 10)}`
				const normalizedCode = code.replace(/\t/g, '    ')

				const container = containerRef.current
				if (container) {
					const errEl = container.querySelector('.error-icon, .error-text, [id^="d-"]')
					if (errEl) errEl.remove()
				}

				const { svg: rendered } = await mermaid.render(id, normalizedCode)
				if (!cancelled) {
					setSvg(rendered)
				}
			} catch (err) {
				console.warn('[MermaidBlock] render error (suppressed):', code.substring(0, 60))
				if (!cancelled) {
					setError(true)
				}
			}
		}

		render()
		return () => { cancelled = true }
	}, [code])

	if (error) {
		return null
	}

	if (!svg) {
		return <div ref={containerRef} className='mermaid-loading animate-pulse bg-gray-100/50 rounded-lg h-20' />
	}

	return <div ref={containerRef}><DiagramViewer kind='svg' svg={svg} title='Mermaid 图谱' /></div>
}
