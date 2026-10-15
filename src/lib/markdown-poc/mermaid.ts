/**
 * Mermaid boundary for the isolated Markdown PoC.
 *
 * The upstream Mermaid renderer emits HTML-bearing SVG constructs in current
 * browsers (`foreignObject`, CSS, filters). The PoC instead owns a deliberately
 * narrow, static flowchart grammar and builds the finite SVG schema directly.
 * This keeps labels and edges usable without admitting third-party markup.
 */

type MermaidNode = {
	id: string
	label: string
}

type MermaidEdge = {
	from: MermaidNode
	to: MermaidNode
}

const nodePattern = /^([A-Za-z][A-Za-z0-9_-]*)(?:\[([\p{L}\p{N} .,!?:()/-]{1,80})\])?$/u
const headerPattern = /^flowchart\s+(LR|RL|TB|BT)$/
const maximumNodes = 16
const maximumEdges = 32

function escapeHtml(value: string): string {
	return value.replace(/[&<>'"]/g, character => {
		const entities: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }
		return entities[character]
	})
}

function parseNode(source: string): MermaidNode | null {
	const match = nodePattern.exec(source.trim())
	if (!match) return null
	return { id: match[1], label: match[2] ?? match[1] }
}

function parseFlowchart(source: string): { direction: string; nodes: MermaidNode[]; edges: MermaidEdge[] } | null {
	if (source.length === 0 || source.length > 4096 || /[<&"'`]/.test(source)) return null
	const lines = source.trim().split('\n')
	const header = headerPattern.exec(lines[0] ?? '')
	if (!header) return null

	const nodes = new Map<string, MermaidNode>()
	const edges: MermaidEdge[] = []
	for (const line of lines.slice(1)) {
		if (line.trim() === '') continue
		const parts = line.split('-->')
		if (parts.length !== 2 || edges.length >= maximumEdges) return null
		const from = parseNode(parts[0])
		const to = parseNode(parts[1])
		if (!from || !to) return null
		for (const node of [from, to]) {
			const existing = nodes.get(node.id)
			if (existing && existing.label !== node.label) return null
			if (!existing && nodes.size >= maximumNodes) return null
			nodes.set(node.id, node)
		}
		edges.push({ from: nodes.get(from.id)!, to: nodes.get(to.id)! })
	}
	return edges.length > 0 ? { direction: header[1], nodes: [...nodes.values()], edges } : null
}

function sourceHash(source: string): string {
	let hash = 2166136261
	for (const character of source) {
		hash ^= character.codePointAt(0)!
		hash = Math.imul(hash, 16777619)
	}
	return (hash >>> 0).toString(36)
}

function coordinate(index: number, direction: string): { x: number; y: number } {
	const horizontal = direction === 'LR' || direction === 'RL'
	const reversed = direction === 'RL' || direction === 'BT'
	const offset = reversed ? maximumNodes - 1 - index : index
	return horizontal ? { x: 24 + offset * 144, y: 24 } : { x: 24, y: 24 + offset * 88 }
}

/**
 * Returns a fully controlled SVG or `null`; callers provide the exact inert
 * fallback so all Markdown outcome accounting stays in render-poc.
 */
export function renderIsolatedMermaidSvg(source: string): string | null {
	const chart = parseFlowchart(source)
	if (!chart) return null
	const horizontal = chart.direction === 'LR' || chart.direction === 'RL'
	const width = horizontal ? 48 + maximumNodes * 144 : 192
	const height = horizontal ? 88 : 48 + maximumNodes * 88
	const rootId = `poc-mermaid-${sourceHash(source)}`
	const markerId = `${rootId}-arrow`
	const indexById = new Map(chart.nodes.map((node, index) => [node.id, index]))
	const edges = chart.edges
		.map((edge, index) => {
			const from = coordinate(indexById.get(edge.from.id)!, chart.direction)
			const to = coordinate(indexById.get(edge.to.id)!, chart.direction)
			const path = horizontal ? `M ${from.x + 112} ${from.y + 20} L ${to.x} ${to.y + 20}` : `M ${from.x + 72} ${from.y + 40} L ${to.x + 72} ${to.y}`
			return `<path id="${rootId}-edge-${index}" d="${path}" fill="none" stroke="#334155" stroke-width="2" marker-end="url(#${markerId})"></path>`
		})
		.join('')
	const nodes = chart.nodes
		.map((node, index) => {
			const point = coordinate(index, chart.direction)
			return `<g id="${rootId}-node-${node.id.toLowerCase()}"><rect x="${point.x}" y="${point.y}" width="112" height="40" rx="6" fill="#eef2ff" stroke="#334155" stroke-width="2"></rect><text x="${point.x + 56}" y="${point.y + 25}" fill="#0f172a" text-anchor="middle">${escapeHtml(node.label)}</text></g>`
		})
		.join('')

	return `<svg data-poc-mermaid="rendered" id="${rootId}" xmlns="http://www.w3.org/2000/svg" role="graphics-document" aria-roledescription="flowchart-v2" viewBox="0 0 ${width} ${height}"><title>Isolated Mermaid flowchart</title><defs><marker id="${markerId}" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M 0 0 L 0 8 L 8 4 z" fill="#334155"></path></marker></defs>${edges}${nodes}</svg>`
}

export function isIsolatedMermaidSource(source: string): boolean {
	return parseFlowchart(source) !== null
}
