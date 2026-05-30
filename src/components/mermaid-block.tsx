'use client'

import { useEffect, useRef, useState } from 'react'

let mermaidPromise: Promise<any> | null = null
let mermaidFailed = false

async function getMermaid(): Promise<any> {
	if (mermaidFailed) throw new Error('mermaid not available')
	if (!mermaidPromise) {
		mermaidPromise = (async () => {
			try {
				const mod = await import(/* webpackIgnore: true */ 'mermaid')
				const m = mod.default ?? mod
				m.initialize({
					startOnLoad: false,
					theme: 'default',
					securityLevel: 'strict',
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

export function MermaidBlock({ code }: { code: string }) {
	const containerRef = useRef<HTMLDivElement>(null)
	const [svg, setSvg] = useState('')
	const [error, setError] = useState(false)

	useEffect(() => {
		let cancelled = false

		async function render() {
			try {
				const mermaid = await getMermaid()
				const id = `mermaid-${Math.random().toString(36).slice(2, 10)}`
				const { svg: rendered } = await mermaid.render(id, code)
				if (!cancelled) {
					setSvg(rendered)
				}
			} catch {
				if (!cancelled) {
					setError(true)
				}
			}
		}

		render()
		return () => { cancelled = true }
	}, [code])

	if (error) {
		return (
			<pre className='mermaid-fallback'>
				<code>{code}</code>
			</pre>
		)
	}

	if (!svg) {
		return <div className='mermaid-loading animate-pulse bg-gray-100/50 rounded-lg h-20' />
	}

	return (
		<div
			ref={containerRef}
			className='mermaid'
			dangerouslySetInnerHTML={{ __html: svg }}
		/>
	)
}
