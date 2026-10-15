import { describe, expect, it, vi } from 'vitest'
import { markRenderReady } from './render-readiness'

describe('render readiness marks', () => {
	it('records one fixed, non-sensitive mark for a committed route state', () => {
		const mark = vi.fn()
		vi.stubGlobal('performance', { getEntriesByName: () => [], mark })

		markRenderReady('notes:list-ready')

		expect(mark).toHaveBeenCalledWith('notes:list-ready')
	})

	it('does not duplicate a readiness mark across re-renders', () => {
		const mark = vi.fn()
		vi.stubGlobal('performance', { getEntriesByName: () => [{ name: 'notes:list-ready' }], mark })

		markRenderReady('notes:list-ready')

		expect(mark).not.toHaveBeenCalled()
	})
})
