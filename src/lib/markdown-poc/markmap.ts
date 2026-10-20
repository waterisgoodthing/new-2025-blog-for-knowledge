/**
 * Markmap boundary for the isolated Markdown PoC.
 *
 * The production Markmap view creates interactive SVG, global CSS, links and
 * download affordances. This PoC accepts only a small heading tree and emits
 * a static, finite SVG itself. Pan, zoom, navigation and download are absent.
 */

type MarkmapNode = {
	level: number
	label: string
	parent: number | null
}

const headingPattern = /^(#{1,3})\s+([\p{L}\p{N} .,!?:()/-]{1,80})$/u
const maximumNodes = 16

function escapeHtml(value: string): string {
	return value.replace(/[&<>'"]/g, character => {
		const entities: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }
		return entities[character]
	})
}

function parseHeadingTree(source: string): MarkmapNode[] | null {
	if (source.length === 0 || source.length > 4096 || /[<&"'`]/.test(source)) return null
	const nodes: MarkmapNode[] = []
	const latestByLevel = new Map<number, number>()
	for (const line of source.trim().split('\n')) {
		const match = headingPattern.exec(line)
		if (!match || nodes.length >= maximumNodes) return null
		const level = match[1].length
		const parent = level === 1 ? null : (latestByLevel.get(level - 1) ?? null)
		if (level > 1 && parent === null) return null
		nodes.push({ level, label: match[2], parent })
		latestByLevel.set(level, nodes.length - 1)
		for (const knownLevel of [...latestByLevel.keys()]) {
			if (knownLevel > level) latestByLevel.delete(knownLevel)
		}
	}
	return nodes.length > 0 && nodes[0].level === 1 ? nodes : null
}

function sourceHash(source: string): string {
	let hash = 2166136261
	for (const character of source) {
		hash ^= character.codePointAt(0)!
		hash = Math.imul(hash, 16777619)
	}
	return (hash >>> 0).toString(36)
}

/** Returns a static final SVG or `null`; callers own the exact text fallback. */
export function renderIsolatedMarkmapSvg(source: string): string | null {
	const nodes = parseHeadingTree(source)
	if (!nodes) return null
	const rootId = `poc-markmap-${sourceHash(source)}`
	const width = 560
	const height = Math.max(96, 32 + nodes.length * 64)
	const points = nodes.map((node, index) => ({ x: 24 + (node.level - 1) * 176, y: 24 + index * 64 }))
	const edges = nodes
		.map((node, index) => {
			if (node.parent === null) return ''
			const parent = points[node.parent]
			const point = points[index]
			return `<path id="${rootId}-edge-${index}" d="M ${parent.x + 144} ${parent.y + 20} L ${point.x} ${point.y + 20}" fill="none" stroke="#475569" stroke-width="2"></path>`
		})
		.join('')
	const renderedNodes = nodes
		.map((node, index) => {
			const point = points[index]
			return `<g id="${rootId}-node-${index}"><rect x="${point.x}" y="${point.y}" width="144" height="40" rx="6" fill="#ecfeff" stroke="#475569" stroke-width="2"></rect><text x="${point.x + 72}" y="${point.y + 25}" fill="#0f172a" text-anchor="middle">${escapeHtml(node.label)}</text></g>`
		})
		.join('')

	return `<svg data-poc-markmap="rendered" id="${rootId}" xmlns="http://www.w3.org/2000/svg" role="graphics-document" aria-roledescription="static-mindmap-v1" viewBox="0 0 ${width} ${height}"><title>Isolated Markmap heading tree</title>${edges}${renderedNodes}</svg>`
}
