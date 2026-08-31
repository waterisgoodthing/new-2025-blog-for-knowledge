export type RenderReadyMark = 'notes:list-ready' | 'notes:detail-ready' | 'manage:auth-submit' | 'manage:content-ready'

export function markRenderReady(name: RenderReadyMark) {
	if (typeof performance === 'undefined' || performance.getEntriesByName(name).length > 0) return
	performance.mark(name)
}
