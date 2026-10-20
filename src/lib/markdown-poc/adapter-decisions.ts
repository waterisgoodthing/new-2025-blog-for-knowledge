/**
 * Explicit M5 adapter decisions for the isolated Markdown PoC.
 * These declarations do not enable production or PoC special renderers.
 */

export type AdapterName = 'math' | 'mermaid' | 'markmap' | 'chart'
export type AdapterDecisionStatus = 'ENABLED_ISOLATED' | 'DEFERRED_INERT'

export type AdapterDecision = {
	status: AdapterDecisionStatus
	reason: string
}

const decisions: Record<AdapterName, AdapterDecision> = {
	math: {
		status: 'ENABLED_ISOLATED',
		reason: 'The M6.3 PoC accepts only a strict KaTeX span/class/attribute/style-value subset and locally falls back for every other result.'
	},
	mermaid: {
		status: 'ENABLED_ISOLATED',
		reason: 'The PoC accepts a bounded static flowchart grammar and constructs its finite SVG schema itself; all other Mermaid input locally falls back.'
	},
	markmap: {
		status: 'ENABLED_ISOLATED',
		reason: 'The PoC accepts a bounded heading tree and constructs its finite static SVG itself; links, pan/zoom, navigation and download are absent.'
	},
	chart: {
		status: 'ENABLED_ISOLATED',
		reason: 'The PoC accepts a bounded bar JSON schema, owns the final Canvas and draws it without functions, HTML, network or download.'
	}
}

export function getAdapterDecision(name: AdapterName): AdapterDecision {
	return decisions[name]
}
