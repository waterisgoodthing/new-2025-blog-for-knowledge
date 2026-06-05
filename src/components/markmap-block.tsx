'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { Maximize2, RotateCcw, X, Download } from 'lucide-react'
import { DialogModal } from '@/components/dialog-modal'

let libPromise: Promise<typeof import('markmap-lib')> | null = null
let viewPromise: Promise<typeof import('markmap-view')> | null = null

async function loadMarkmapLib() {
	if (!libPromise) {
		libPromise = import('markmap-lib').catch(err => {
			console.warn('Failed to load markmap-lib:', err)
			libPromise = null
			throw err
		})
	}
	return libPromise
}

async function loadMarkmapView() {
	if (!viewPromise) {
		viewPromise = import('markmap-view').catch(err => {
			console.warn('Failed to load markmap-view:', err)
			viewPromise = null
			throw err
		})
	}
	return viewPromise
}

function IconButton({ label, onClick, children }: { label: string; onClick: () => void; children: React.ReactNode }) {
	return (
		<button type='button' className='inline-flex h-8 w-8 items-center justify-center rounded-md text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-950 active:scale-95' onClick={onClick} aria-label={label} title={label}>
			{children}
		</button>
	)
}

async function renderIntoSvg(svgEl: SVGSVGElement, code: string): Promise<any> {
	const [lib, view] = await Promise.all([loadMarkmapLib(), loadMarkmapView()])
	const { Transformer } = lib
	const { Markmap } = view
	const transformer = new Transformer()
	const { root } = transformer.transform(code)
	const mm = Markmap.create(svgEl, {
		autoFit: true,
		duration: 200,
		embedGlobalCSS: true,
		initialExpandLevel: 3,
		pan: true,
		zoom: true,
		toggleRecursively: false,
	}, root)
	return mm
}

const MAX_RETRIES = 3

export function MarkmapBlock({ code }: { code: string }) {
	const previewSvgRef = useRef<SVGSVGElement>(null)
	const fullscreenSvgRef = useRef<SVGSVGElement>(null)
	const previewMmRef = useRef<any>(null)
	const fullscreenMmRef = useRef<any>(null)
	const [error, setError] = useState(false)
	const [retryCount, setRetryCount] = useState(0)
	const [open, setOpen] = useState(false)
	const [mounted, setMounted] = useState(false)

	useEffect(() => {
		setMounted(true)
	}, [])

	useEffect(() => {
		if (!mounted || !previewSvgRef.current) return
		let cancelled = false
		setError(false)
		renderIntoSvg(previewSvgRef.current, code).then(mm => {
			if (!cancelled) previewMmRef.current = mm
		}).catch(() => {
			if (!cancelled) setError(true)
		})
		return () => {
			cancelled = true
			if (previewMmRef.current) { previewMmRef.current.destroy(); previewMmRef.current = null }
		}
	}, [code, mounted, retryCount])

	useEffect(() => {
		if (!open || !fullscreenSvgRef.current) return
		let cancelled = false
		renderIntoSvg(fullscreenSvgRef.current, code).then(mm => {
			if (!cancelled) fullscreenMmRef.current = mm
		}).catch(() => {})
		return () => {
			cancelled = true
			if (fullscreenMmRef.current) { fullscreenMmRef.current.destroy(); fullscreenMmRef.current = null }
		}
	}, [open, code])

	const handleDownload = useCallback(() => {
		const svgEl = previewSvgRef.current
		if (!svgEl) return
		const svgData = new XMLSerializer().serializeToString(svgEl)
		const blob = new Blob([svgData], { type: 'image/svg+xml' })
		const url = URL.createObjectURL(blob)
		const a = document.createElement('a')
		a.href = url
		a.download = 'markmap.svg'
		a.click()
		URL.revokeObjectURL(url)
	}, [])

	const handleFit = useCallback(() => {
		if (fullscreenMmRef.current) fullscreenMmRef.current.fit()
	}, [])

	const handleClose = useCallback(() => {
		if (fullscreenMmRef.current) { fullscreenMmRef.current.destroy(); fullscreenMmRef.current = null }
		setOpen(false)
	}, [])

	const handleRetry = useCallback(() => {
		if (retryCount < MAX_RETRIES) {
			setRetryCount(c => c + 1)
		}
	}, [retryCount])

	if (!mounted) {
		return (
			<div className='my-6 h-[200px] w-full animate-pulse rounded-lg border border-zinc-200/70 bg-zinc-100' />
		)
	}

	if (error) {
		return (
			<div className='my-6 rounded-lg border border-zinc-200/70 bg-zinc-50/70 p-4'>
				<p className='mb-2 text-sm text-zinc-500'>思维导图渲染失败</p>
				{retryCount < MAX_RETRIES && (
					<button
						type='button'
						onClick={handleRetry}
						className='mb-3 inline-flex items-center gap-1.5 rounded-lg bg-zinc-200/70 px-3 py-1.5 text-xs font-medium text-zinc-700 transition-colors hover:bg-zinc-300/70'
					>
						<RotateCcw size={13} />
						重试 ({retryCount}/{MAX_RETRIES})
					</button>
				)}
				<pre className='overflow-x-auto rounded-md bg-zinc-100 p-3 text-xs text-zinc-600'>
					<code>{code}</code>
				</pre>
			</div>
		)
	}

	return (
		<figure className='diagram-viewer my-6 w-full'>
			<div className='mb-2 flex items-center justify-between gap-3 text-xs text-zinc-500'>
				<figcaption className='min-w-0 truncate'>思维导图</figcaption>
				<div className='flex shrink-0 items-center gap-1'>
					<IconButton label='下载 SVG' onClick={handleDownload}>
						<Download size={16} />
					</IconButton>
					<IconButton label='全屏查看' onClick={() => setOpen(true)}>
						<Maximize2 size={16} />
					</IconButton>
				</div>
			</div>
			<div className='diagram-stage block w-full overflow-hidden rounded-lg border border-zinc-200/70 bg-zinc-50/70 p-3 text-left transition hover:border-zinc-300'>
				<svg ref={previewSvgRef} className='h-auto w-full' style={{ minHeight: 200, minWidth: 300 }} />
			</div>

			<DialogModal open={open} onClose={handleClose} className='h-[92vh] w-[94vw] max-w-none bg-white p-0' overlayClassName='bg-white/80'>
				<div className='flex h-full flex-col'>
					<div className='flex h-12 shrink-0 items-center justify-between border-b border-zinc-200 px-3'>
						<div className='min-w-0 truncate text-sm font-medium text-zinc-700'>思维导图</div>
						<div className='flex items-center gap-1'>
							<IconButton label='适配' onClick={handleFit}>
								<RotateCcw size={16} />
							</IconButton>
							<IconButton label='下载 SVG' onClick={handleDownload}>
								<Download size={16} />
							</IconButton>
							<button
								type='button'
								onClick={handleClose}
								className='ml-2 inline-flex h-8 w-8 items-center justify-center rounded-md text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-950'
								aria-label='关闭'
								title='关闭'
							>
								<X size={17} />
							</button>
						</div>
					</div>
					<div className='min-h-0 flex-1 overflow-hidden bg-zinc-50 p-4'>
						<svg ref={fullscreenSvgRef} className='h-full w-full' />
					</div>
				</div>
			</DialogModal>
		</figure>
	)
}
