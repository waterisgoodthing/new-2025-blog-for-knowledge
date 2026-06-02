'use client'

import { useMemo, useState, type ReactNode } from 'react'
import { ExternalLink, Maximize2, Minus, Plus, RotateCcw, X } from 'lucide-react'
import { DialogModal } from '@/components/dialog-modal'
import { cn } from '@/lib/utils'

type DiagramViewerProps =
	| {
			kind: 'image'
			src: string
			alt?: string
			title?: string
	  }
	| {
			kind: 'svg'
			svg: string
			title?: string
	  }

const ZOOM_STEP = 0.25
const MIN_ZOOM = 0.5
const MAX_ZOOM = 3

function clampZoom(value: number) {
	return Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, value))
}

function IconButton({ label, onClick, children, href }: { label: string; onClick?: () => void; children: ReactNode; href?: string }) {
	const className = 'inline-flex h-8 w-8 items-center justify-center rounded-md text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-950 active:scale-95'

	if (href) {
		return (
			<a className={className} href={href} target='_blank' rel='noopener noreferrer' aria-label={label} title={label}>
				{children}
			</a>
		)
	}

	return (
		<button type='button' className={className} onClick={onClick} aria-label={label} title={label}>
			{children}
		</button>
	)
}

export function DiagramViewer(props: DiagramViewerProps) {
	const [open, setOpen] = useState(false)
	const [zoom, setZoom] = useState(1)
	const title = props.title || (props.kind === 'image' ? props.alt : '') || '图谱'
	const svgDataUrl = useMemo(() => {
		if (props.kind !== 'svg') return ''
		return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(props.svg)}`
	}, [props])

	const zoomIn = () => setZoom(value => clampZoom(value + ZOOM_STEP))
	const zoomOut = () => setZoom(value => clampZoom(value - ZOOM_STEP))
	const reset = () => setZoom(1)

	const preview = props.kind === 'image'
		? <img src={props.src} alt={props.alt || ''} title={props.title} loading='lazy' className='diagram-media max-h-[72vh] w-full object-contain' />
		: <div className='diagram-media diagram-svg' dangerouslySetInnerHTML={{ __html: props.svg }} />

	const fullView = props.kind === 'image'
		? <img src={props.src} alt={props.alt || ''} className='diagram-media max-w-none object-contain' style={{ transform: `scale(${zoom})`, transformOrigin: 'top left' }} />
		: <div className='diagram-media diagram-svg max-w-none' style={{ transform: `scale(${zoom})`, transformOrigin: 'top left' }} dangerouslySetInnerHTML={{ __html: props.svg }} />

	return (
		<figure className='diagram-viewer my-6 w-full'>
			<div className='mb-2 flex items-center justify-between gap-3 text-xs text-zinc-500'>
				<figcaption className='min-w-0 truncate'>{title}</figcaption>
				<div className='flex shrink-0 items-center gap-1'>
					{props.kind === 'image' && (
						<IconButton label='打开原图' href={props.src}>
							<ExternalLink size={16} />
						</IconButton>
					)}
					{props.kind === 'svg' && (
						<IconButton label='下载 SVG' href={svgDataUrl}>
							<ExternalLink size={16} />
						</IconButton>
					)}
					<IconButton label='全屏查看' onClick={() => setOpen(true)}>
						<Maximize2 size={16} />
					</IconButton>
				</div>
			</div>
			<button
				type='button'
				onClick={() => setOpen(true)}
				className='diagram-stage block w-full overflow-auto rounded-lg border border-zinc-200/70 bg-zinc-50/70 p-3 text-left transition hover:border-zinc-300'
				aria-label='全屏查看图谱'
			>
				{preview}
			</button>

			<DialogModal open={open} onClose={() => setOpen(false)} className='h-[92vh] w-[94vw] max-w-none bg-white p-0' overlayClassName='bg-white/80'>
				<div className='flex h-full flex-col'>
					<div className='flex h-12 shrink-0 items-center justify-between border-b border-zinc-200 px-3'>
						<div className='min-w-0 truncate text-sm font-medium text-zinc-700'>{title}</div>
						<div className='flex items-center gap-1'>
							<IconButton label='缩小' onClick={zoomOut}><Minus size={16} /></IconButton>
							<span className='w-12 text-center text-xs tabular-nums text-zinc-500'>{Math.round(zoom * 100)}%</span>
							<IconButton label='放大' onClick={zoomIn}><Plus size={16} /></IconButton>
							<IconButton label='重置' onClick={reset}><RotateCcw size={16} /></IconButton>
							<button
								type='button'
								onClick={() => setOpen(false)}
								className={cn('ml-2 inline-flex h-8 w-8 items-center justify-center rounded-md text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-950')}
								aria-label='关闭'
								title='关闭'
							>
								<X size={17} />
							</button>
						</div>
					</div>
					<div className='min-h-0 flex-1 overflow-auto bg-zinc-50 p-4'>
						{fullView}
					</div>
				</div>
			</DialogModal>
		</figure>
	)
}
