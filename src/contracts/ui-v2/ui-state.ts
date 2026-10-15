// UI-facing contract: page/async state (F4 skeleton).
// Mirrors the Week1 AsyncStatePanel semantics (loading/empty/error/retry)
// without importing business logic.

export type PageState = 'loading' | 'ready' | 'empty' | 'error' | 'partial'

export interface UiPageModel<T> {
	state: PageState
	data: T | null
	error: string | null
	/** Data provenance; mocks must use 'mock'. */
	source: 'backend' | 'mock' | 'estimated'
}
