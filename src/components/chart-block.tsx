'use client'

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Maximize2, X, Download } from 'lucide-react'
import { DialogModal } from '@/components/dialog-modal'

const ALLOWED_CHART_TYPES = ['bar', 'line', 'pie', 'radar'] as const
type ChartType = typeof ALLOWED_CHART_TYPES[number]

const MAX_DATA_LENGTH = 1000

type SafeChartOption = {
	type: ChartType
	title?: string
	xAxis?: string[]
	categories?: string[]
	series?: Array<{ name?: string; data: number[] }>
	legend?: string[]
	data?: Array<{ name: string; value: number }>
}

function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function toText(value: unknown): string | undefined {
	return typeof value === 'string' ? value.slice(0, 80) : undefined
}

function toStringArray(value: unknown): string[] | undefined {
	if (!Array.isArray(value)) return undefined
	const result = value.slice(0, MAX_DATA_LENGTH).filter((item): item is string => typeof item === 'string')
	return result.length === value.slice(0, MAX_DATA_LENGTH).length ? result : undefined
}

function toNumberArray(value: unknown): number[] | undefined {
	if (!Array.isArray(value)) return undefined
	const result = value.slice(0, MAX_DATA_LENGTH).filter((item): item is number => typeof item === 'number' && Number.isFinite(item))
	return result.length === value.slice(0, MAX_DATA_LENGTH).length ? result : undefined
}

function toPieData(value: unknown): Array<{ name: string; value: number }> | undefined {
	if (!Array.isArray(value)) return undefined
	const result = value.slice(0, MAX_DATA_LENGTH).map(item => {
		if (!isRecord(item)) return null
		const name = toText(item.name)
		const pointValue = item.value
		if (!name || typeof pointValue !== 'number' || !Number.isFinite(pointValue)) return null
		return { name, value: pointValue }
	})
	if (result.some(item => item === null)) return undefined
	return result as Array<{ name: string; value: number }>
}

function toSeries(value: unknown): Array<{ name?: string; data: number[] }> | undefined {
	if (!Array.isArray(value)) return undefined
	const result = value.slice(0, 20).map(item => {
		if (!isRecord(item)) return null
		const data = toNumberArray(item.data)
		if (!data) return null
		return { name: toText(item.name), data }
	})
	if (result.some(item => item === null)) return undefined
	return result as Array<{ name?: string; data: number[] }>
}

function parseChartOption(raw: string): SafeChartOption | null {
	try {
		const parsed = JSON.parse(raw)
		if (!isRecord(parsed) || !ALLOWED_CHART_TYPES.includes(parsed.type as ChartType)) return null

		const safe: SafeChartOption = {
			type: parsed.type as ChartType,
			title: toText(parsed.title),
			xAxis: toStringArray(parsed.xAxis),
			categories: toStringArray(parsed.categories),
			legend: toStringArray(Array.isArray(parsed.legend) ? parsed.legend : isRecord(parsed.legend) ? parsed.legend.data : undefined),
			series: toSeries(parsed.series),
			data: toPieData(parsed.data),
		}

		if (safe.type === 'pie') {
			if (!safe.data && !safe.series?.[0]?.data) return null
			return safe
		}

		if (!safe.series?.length) return null
		if ((safe.type === 'bar' || safe.type === 'line') && !(safe.xAxis?.length || safe.categories?.length)) return null
		if (safe.type === 'radar' && !(safe.categories?.length || safe.xAxis?.length)) return null
		return safe
	} catch {
		return null
	}
}

function buildEChartsOption(safe: SafeChartOption): Record<string, unknown> {
	const brandColor = getComputedStyle(document.documentElement).getPropertyValue('--color-brand').trim() || '#3b82f6'
	const colors = [brandColor, '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

	if (safe.type === 'pie') {
		return {
			tooltip: { trigger: 'item' },
			legend: safe.legend ? { data: safe.legend } : undefined,
			series: [{
				type: 'pie',
				radius: '50%',
				data: safe.data || (safe.series?.[0]?.data?.map((v, i) => ({ name: safe.categories?.[i] || `项${i + 1}`, value: v })) ?? []),
				emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.2)' } },
			}],
			color: colors,
		}
	}

	if (safe.type === 'radar') {
		return {
			tooltip: {},
			legend: safe.legend ? { data: safe.legend } : undefined,
			radar: { indicator: (safe.categories || safe.xAxis || []).map(c => ({ name: c, max: 100 })) },
			series: [{
				type: 'radar',
				data: safe.series?.map(s => ({ name: s.name, value: s.data })) ?? [],
			}],
			color: colors,
		}
	}

	return {
		tooltip: { trigger: 'axis' },
		legend: safe.legend ? { data: safe.legend } : undefined,
		xAxis: { type: 'category', data: safe.xAxis || safe.categories || [] },
		yAxis: { type: 'value' },
		series: safe.series?.map(s => ({ ...s, type: safe.type })) ?? [],
		color: colors,
	}
}

function IconButton({ label, onClick, children }: { label: string; onClick: () => void; children: React.ReactNode }) {
	return (
		<button type='button' className='inline-flex h-8 w-8 items-center justify-center rounded-md text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-950 active:scale-95' onClick={onClick} aria-label={label} title={label}>
			{children}
		</button>
	)
}

let ReactEChartsCore: any = null
let echartsLoaded = false

function LazyECharts({ option, style }: { option: Record<string, unknown>; style?: React.CSSProperties }) {
	const [Comp, setComp] = useState<any>(null)

	useEffect(() => {
		let cancelled = false
		if (echartsLoaded && ReactEChartsCore) {
			setComp(() => ReactEChartsCore)
			return () => { cancelled = true }
		}
		Promise.all([
			import('echarts/core'),
			import('echarts/charts'),
			import('echarts/components'),
			import('echarts/renderers'),
			import('echarts-for-react'),
		]).then(([core, charts, components, renderers, reactEcharts]) => {
			const echarts = core
			echarts.use([
				charts.BarChart,
				charts.LineChart,
				charts.PieChart,
				charts.RadarChart,
				components.GridComponent,
				components.TooltipComponent,
				components.LegendComponent,
				components.TitleComponent,
				components.RadarComponent,
				renderers.CanvasRenderer,
			])
			ReactEChartsCore = reactEcharts.default
			echartsLoaded = true
			if (!cancelled) setComp(() => reactEcharts.default)
		}).catch(err => {
			console.warn('[ChartBlock] Failed to load echarts:', err)
		})
		return () => { cancelled = true }
	}, [])

	if (!Comp) return <div className='h-[400px] animate-pulse rounded-lg bg-gray-100/50' />
	return <Comp option={option} style={style} opts={{ renderer: 'canvas' }} />
}

export function ChartBlock({ code }: { code: string }) {
	const [open, setOpen] = useState(false)
	const figureRef = useRef<HTMLElement>(null)
	const safeOption = useMemo(() => parseChartOption(code), [code])
	const echartsOption = useMemo(() => safeOption ? buildEChartsOption(safeOption) : null, [safeOption])

	const handleDownload = useCallback(() => {
		const canvas = figureRef.current?.querySelector('canvas') as HTMLCanvasElement | null
		if (!canvas) return
		const url = canvas.toDataURL('image/png')
		const a = document.createElement('a')
		a.href = url
		a.download = 'chart.png'
		a.click()
	}, [])

	if (!safeOption || !echartsOption) {
		return (
			<pre className='chart-fallback'>
				<code>{code}</code>
			</pre>
		)
	}

	return (
		<figure ref={figureRef} className='chart-viewer my-6 w-full'>
			<div className='mb-2 flex items-center justify-between gap-3 text-xs text-zinc-500'>
				<figcaption className='min-w-0 truncate'>{safeOption.title || '数据图表'}</figcaption>
				<div className='flex shrink-0 items-center gap-1'>
					<IconButton label='下载 PNG' onClick={handleDownload}>
						<Download size={16} />
					</IconButton>
					<IconButton label='全屏查看' onClick={() => setOpen(true)}>
						<Maximize2 size={16} />
					</IconButton>
				</div>
			</div>
			<div className='overflow-hidden rounded-lg border border-zinc-200/70 bg-zinc-50/70 p-3'>
				<LazyECharts option={echartsOption} style={{ height: 400, width: '100%' }} />
			</div>

			<DialogModal open={open} onClose={() => setOpen(false)} className='h-[92vh] w-[94vw] max-w-none bg-white p-0' overlayClassName='bg-white/80'>
				<div className='flex h-full flex-col'>
					<div className='flex h-12 shrink-0 items-center justify-between border-b border-zinc-200 px-3'>
						<div className='min-w-0 truncate text-sm font-medium text-zinc-700'>{safeOption.title || '数据图表'}</div>
						<div className='flex items-center gap-1'>
							<IconButton label='下载 PNG' onClick={handleDownload}>
								<Download size={16} />
							</IconButton>
							<button
								type='button'
								onClick={() => setOpen(false)}
								className='ml-2 inline-flex h-8 w-8 items-center justify-center rounded-md text-zinc-600 transition hover:bg-zinc-100 hover:text-zinc-950'
								aria-label='关闭'
								title='关闭'
							>
								<X size={17} />
							</button>
						</div>
					</div>
					<div className='min-h-0 flex-1 overflow-hidden bg-zinc-50 p-4'>
						<LazyECharts option={echartsOption} style={{ height: '100%', width: '100%' }} />
					</div>
				</div>
			</DialogModal>
		</figure>
	)
}
