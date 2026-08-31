/** Bounded Canvas chart boundary for the isolated Markdown PoC. */

type ChartConfig = { type: 'bar'; xAxis: string[]; series: Array<{ name?: string; data: number[] }> }

function validLabel(value: unknown): value is string {
	return typeof value === 'string' && /^[\p{L}\p{N} .,!?:()/-]{1,40}$/u.test(value)
}

function parseChart(source: string): ChartConfig | null {
	if (source.length === 0 || source.length > 4096) return null
	try {
		const value: unknown = JSON.parse(source)
		if (!value || typeof value !== 'object' || Array.isArray(value)) return null
		const record = value as Record<string, unknown>
		if (
			Object.keys(record).some(key => !['type', 'xAxis', 'series'].includes(key)) ||
			record.type !== 'bar' ||
			!Array.isArray(record.xAxis) ||
			!Array.isArray(record.series)
		)
			return null
		if (record.xAxis.length < 1 || record.xAxis.length > 12 || !record.xAxis.every(validLabel) || record.series.length < 1 || record.series.length > 4)
			return null
		const xAxis = record.xAxis as string[]
		const series = record.series.map(item => {
			if (!item || typeof item !== 'object' || Array.isArray(item)) return null
			const entry = item as Record<string, unknown>
			if (
				Object.keys(entry).some(key => key !== 'name' && key !== 'data') ||
				(entry.name !== undefined && !validLabel(entry.name)) ||
				!Array.isArray(entry.data)
			)
				return null
			const data = entry.data
			if (data.length !== xAxis.length || !data.every(number => typeof number === 'number' && Number.isFinite(number) && Math.abs(number) <= 1_000_000))
				return null
			return { name: entry.name as string | undefined, data: data as number[] }
		})
		return series.some(entry => entry === null) ? null : { type: 'bar', xAxis, series: series as ChartConfig['series'] }
	} catch {
		return null
	}
}

export function renderIsolatedChartCanvas(source: string): string | null {
	return parseChart(source)
		? `<canvas data-poc-chart="rendered" data-poc-chart-source="${encodeURIComponent(source)}" width="320" height="180" role="img" aria-label="Isolated static bar chart"></canvas>`
		: null
}

export function drawIsolatedChart(canvas: HTMLCanvasElement, encodedSource: string): boolean {
	let source = ''
	try {
		source = decodeURIComponent(encodedSource)
	} catch {
		return false
	}
	const chart = parseChart(source)
	const context = chart ? canvas.getContext('2d') : null
	if (!chart || !context) return false
	context.clearRect(0, 0, canvas.width, canvas.height)
	context.fillStyle = '#ffffff'
	context.fillRect(0, 0, canvas.width, canvas.height)
	const maximum = Math.max(1, ...chart.series.flatMap(series => series.data.map(value => Math.max(0, value))))
	const groupWidth = 250 / chart.xAxis.length
	const barWidth = Math.max(4, (groupWidth - 8) / chart.series.length)
	const colors = ['#2563eb', '#059669', '#d97706', '#7c3aed']
	chart.series.forEach((series, seriesIndex) =>
		series.data.forEach((value, index) => {
			const height = (Math.max(0, value) / maximum) * 120
			context.fillStyle = colors[seriesIndex]
			context.fillRect(42 + index * groupWidth + 4 + seriesIndex * barWidth, 150 - height, barWidth - 1, height)
		})
	)
	context.strokeStyle = '#334155'
	context.beginPath()
	context.moveTo(40, 150)
	context.lineTo(300, 150)
	context.stroke()
	canvas.dataset.pocChartDrawn = 'true'
	return true
}
