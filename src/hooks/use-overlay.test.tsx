import { useRef, useState } from 'react'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { OVERLAY_Z_BASE, OVERLAY_Z_STEP, resetOverlayState, useOverlay, usePrefersReducedMotion, type UseOverlayOptions } from './use-overlay'

interface HarnessProps extends Omit<UseOverlayOptions, 'open' | 'onClose'> {
	open: boolean
	onClose: () => void
	label?: string
}

function OverlayHarness({ open, onClose, label = 'Overlay', ...options }: HarnessProps) {
	const overlay = useOverlay({ open, onClose, ...options })
	if (!open) return null

	return (
		<div data-testid={`${label}-backdrop`} onClick={overlay.handleBackdropClick} style={{ zIndex: overlay.backdropZIndex }}>
			<div
				ref={overlay.containerRef}
				role='dialog'
				aria-modal='true'
				aria-labelledby={overlay.titleId}
				aria-describedby={overlay.descriptionId}
				data-testid={`${label}-dialog`}
				data-z-index={overlay.zIndex}
				data-topmost={String(overlay.isTopmost)}
				style={{ zIndex: overlay.zIndex }}>
				<h2 id={overlay.titleId}>{label} title</h2>
				<p id={overlay.descriptionId}>{label} description</p>
				<button type='button'>{label} first</button>
				<input aria-label={`${label} field`} />
				<button type='button'>{label} last</button>
			</div>
		</div>
	)
}

function focusInitialTriggerWithOpen(props: Partial<HarnessProps> = {}) {
	function Wrapper() {
		const [open, setOpen] = useState(false)
		return (
			<>
				<button type='button' onClick={() => setOpen(true)}>
					trigger
				</button>
				<OverlayHarness {...props} open={open} onClose={() => setOpen(false)} />
			</>
		)
	}
	return render(<Wrapper />)
}

const getDialog = (label = 'Overlay') => screen.getByTestId(`${label}-dialog`)

beforeEach(() => {
	resetOverlayState()
})

afterEach(() => {
	resetOverlayState()
	vi.restoreAllMocks()
})

describe('useOverlay — semantics', () => {
	it('exposes dialog role with an accessible name and description', () => {
		render(<OverlayHarness open onClose={vi.fn()} />)

		const dialog = screen.getByRole('dialog', { name: 'Overlay title' })
		expect(dialog).toHaveAttribute('aria-modal', 'true')
		expect(dialog).toHaveAccessibleDescription('Overlay description')
		expect(dialog.getAttribute('aria-labelledby')).toBe(screen.getByText('Overlay title').id)
	})

	it('reports a stacking z-index at or above the documented overlay base', () => {
		render(<OverlayHarness open onClose={vi.fn()} />)
		expect(Number(getDialog().dataset.zIndex)).toBeGreaterThanOrEqual(OVERLAY_Z_BASE)
	})
})

describe('useOverlay — focus management', () => {
	it('moves focus to the first focusable element on open', async () => {
		render(<OverlayHarness open onClose={vi.fn()} />)
		await waitFor(() => expect(screen.getByText('Overlay first')).toHaveFocus())
	})

	it('honours an explicit initial focus target', async () => {
		function WithInitialFocus() {
			const fieldRef = useRef<HTMLInputElement>(null)
			const overlay = useOverlay({ open: true, onClose: vi.fn(), initialFocusRef: fieldRef as React.RefObject<HTMLElement | null> })
			return (
				<div ref={overlay.containerRef} role='dialog' aria-label='explicit'>
					<button type='button'>first</button>
					<input ref={fieldRef} aria-label='field' />
				</div>
			)
		}
		render(<WithInitialFocus />)
		await waitFor(() => expect(screen.getByLabelText('field')).toHaveFocus())
	})

	it('wraps Tab from the last element to the first', async () => {
		render(<OverlayHarness open onClose={vi.fn()} />)
		const last = screen.getByText('Overlay last')
		last.focus()
		await waitFor(() => expect(last).toHaveFocus())

		fireEvent.keyDown(document, { key: 'Tab' })
		expect(screen.getByText('Overlay first')).toHaveFocus()
	})

	it('wraps Shift+Tab from the first element to the last', async () => {
		render(<OverlayHarness open onClose={vi.fn()} />)
		const first = screen.getByText('Overlay first')
		await waitFor(() => expect(first).toHaveFocus())

		fireEvent.keyDown(document, { key: 'Tab', shiftKey: true })
		expect(screen.getByText('Overlay last')).toHaveFocus()
	})

	it('restores focus to the trigger after closing', async () => {
		const { getByText } = focusInitialTriggerWithOpen()
		const trigger = getByText('trigger')
		trigger.focus()
		fireEvent.click(trigger)
		await waitFor(() => expect(screen.getByText('Overlay first')).toHaveFocus())

		fireEvent.keyDown(document, { key: 'Escape' })
		await waitFor(() => expect(trigger).toHaveFocus())
	})
})

describe('useOverlay — focusability filtering', () => {
	it('wraps past hidden and inert controls instead of escaping the dialog', async () => {
		function WithHiddenTail() {
			const overlay = useOverlay({ open: true, onClose: vi.fn() })
			return (
				<div ref={overlay.containerRef} role='dialog' aria-label='filtered'>
					<button type='button'>first visible</button>
					<button type='button' hidden>
						hidden tail
					</button>
					<div inert>
						<button type='button'>inert tail</button>
					</div>
				</div>
			)
		}
		render(<WithHiddenTail />)

		const first = screen.getByRole('button', { name: 'first visible' })
		await waitFor(() => expect(first).toHaveFocus())

		// Only one tabbable candidate: Tab must be intercepted and keep focus put.
		fireEvent.keyDown(document, { key: 'Tab' })
		expect(first).toHaveFocus()
	})
})

describe('useOverlay — dismissal', () => {
	it('closes on Escape', () => {
		const onClose = vi.fn()
		render(<OverlayHarness open onClose={onClose} />)
		fireEvent.keyDown(document, { key: 'Escape' })
		expect(onClose).toHaveBeenCalledTimes(1)
	})

	it('does not close on Escape when closeOnEscape is false', () => {
		const onClose = vi.fn()
		render(<OverlayHarness open onClose={onClose} closeOnEscape={false} />)
		fireEvent.keyDown(document, { key: 'Escape' })
		expect(onClose).not.toHaveBeenCalled()
	})

	it('closes on a backdrop click', () => {
		const onClose = vi.fn()
		render(<OverlayHarness open onClose={onClose} />)
		fireEvent.click(screen.getByTestId('Overlay-backdrop'))
		expect(onClose).toHaveBeenCalledTimes(1)
	})

	it('does not close when the click originates inside the dialog', () => {
		const onClose = vi.fn()
		render(<OverlayHarness open onClose={onClose} />)
		fireEvent.click(getDialog())
		expect(onClose).not.toHaveBeenCalled()
	})

	it('respects closeOnBackdropClick=false', () => {
		const onClose = vi.fn()
		render(<OverlayHarness open onClose={onClose} closeOnBackdropClick={false} />)
		fireEvent.click(screen.getByTestId('Overlay-backdrop'))
		expect(onClose).not.toHaveBeenCalled()
	})
})

describe('useOverlay — scroll lock', () => {
	it('locks body scroll while open and releases it on close', async () => {
		const { rerender } = render(<OverlayHarness open onClose={vi.fn()} />)
		await waitFor(() => expect(document.body.style.overflow).toBe('hidden'))

		rerender(<OverlayHarness open={false} onClose={vi.fn()} />)
		await waitFor(() => expect(document.body.style.overflow).toBe(''))
	})

	it('keeps the lock while a nested overlay is still open', async () => {
		const { rerender } = render(
			<>
				<OverlayHarness open onClose={vi.fn()} label='outer' />
				<OverlayHarness open onClose={vi.fn()} label='inner' />
			</>
		)
		await waitFor(() => expect(document.body.style.overflow).toBe('hidden'))

		rerender(
			<>
				<OverlayHarness open onClose={vi.fn()} label='outer' />
				<OverlayHarness open={false} onClose={vi.fn()} label='inner' />
			</>
		)
		await waitFor(() => expect(document.body.style.overflow).toBe('hidden'))
	})
})

describe('useOverlay — nesting', () => {
	it('stacks a later overlay above an earlier one and restores ordering when it closes', async () => {
		const outerClose = vi.fn()
		const innerClose = vi.fn()

		const { rerender } = render(
			<>
				<OverlayHarness open onClose={outerClose} label='outer' />
				<OverlayHarness open onClose={innerClose} label='inner' />
			</>
		)

		await waitFor(() => expect(Number(getDialog('inner').dataset.zIndex)).toBeGreaterThan(Number(getDialog('outer').dataset.zIndex)))
		expect(getDialog('inner')).toHaveAttribute('data-topmost', 'true')
		expect(getDialog('outer')).toHaveAttribute('data-topmost', 'false')

		// Escape only dismisses the innermost overlay.
		fireEvent.keyDown(document, { key: 'Escape' })
		expect(innerClose).toHaveBeenCalledTimes(1)
		expect(outerClose).not.toHaveBeenCalled()

		rerender(
			<>
				<OverlayHarness open onClose={outerClose} label='outer' />
				<OverlayHarness open={false} onClose={innerClose} label='inner' />
			</>
		)

		await waitFor(() => expect(getDialog('outer')).toHaveAttribute('data-topmost', 'true'))
		expect(Number(getDialog('outer').dataset.zIndex)).toBe(OVERLAY_Z_BASE)
	})

	it('lets only the topmost overlay trap Tab', async () => {
		render(
			<>
				<OverlayHarness open onClose={vi.fn()} label='outer' />
				<OverlayHarness open onClose={vi.fn()} label='inner' />
			</>
		)

		const innerFirst = screen.getByText('inner first')
		const innerLast = screen.getByText('inner last')
		await waitFor(() => expect(innerFirst).toHaveFocus())

		// Mid-list Tab is a no-op for the inner trap. If the outer trap were also
		// bound it would grab focus (focus is not inside the outer container) and
		// this assertion fails — that is what makes the test discriminating.
		innerFirst.focus()
		fireEvent.keyDown(document, { key: 'Tab' })
		expect(innerFirst).toHaveFocus()

		// And the inner trap still wraps onto itself.
		innerLast.focus()
		fireEvent.keyDown(document, { key: 'Tab' })
		expect(innerFirst).toHaveFocus()
		expect(screen.getByText('outer first')).not.toHaveFocus()
	})

	it('does not steal focus when a non-topmost overlay closes', async () => {
		const outerClose = vi.fn()
		const { rerender } = render(
			<>
				<OverlayHarness open onClose={outerClose} label='outer' />
				<OverlayHarness open onClose={vi.fn()} label='inner' />
			</>
		)
		await waitFor(() => expect(screen.getByText('inner first')).toHaveFocus())

		rerender(
			<>
				<OverlayHarness open={false} onClose={outerClose} label='outer' />
				<OverlayHarness open onClose={vi.fn()} label='inner' />
			</>
		)

		// Focus must remain inside the still-open inner overlay.
		await waitFor(() => expect(screen.getByTestId('inner-dialog').contains(document.activeElement)).toBe(true))
		expect(screen.queryByText('outer first')).not.toBeInTheDocument()
	})

	it('steps the stack by the documented increment per level', async () => {
		render(
			<>
				<OverlayHarness open onClose={vi.fn()} label='one' />
				<OverlayHarness open onClose={vi.fn()} label='two' />
			</>
		)
		await waitFor(() => expect(Number(getDialog('two').dataset.zIndex) - Number(getDialog('one').dataset.zIndex)).toBe(OVERLAY_Z_STEP))
	})
})

describe('usePrefersReducedMotion', () => {
	it('reflects the reduced-motion media query', async () => {
		vi.stubGlobal(
			'matchMedia',
			vi.fn().mockImplementation((query: string) => ({
				matches: query.includes('reduce'),
				media: query,
				onchange: null,
				addEventListener: vi.fn(),
				removeEventListener: vi.fn(),
				addListener: vi.fn(),
				removeListener: vi.fn(),
				dispatchEvent: vi.fn()
			}))
		)

		function Probe() {
			const reduced = usePrefersReducedMotion()
			return <span data-testid='probe'>{String(reduced)}</span>
		}

		render(<Probe />)
		await waitFor(() => expect(screen.getByTestId('probe')).toHaveTextContent('true'))

		vi.unstubAllGlobals()
	})
})

describe('useOverlay — background isolation without an AppShell', () => {
	it('inerts unrelated body children but never the portal host or the toast region', async () => {
		const portalHost = document.createElement('div')
		portalHost.setAttribute('data-uiv2-portal-root', '')
		const toaster = document.createElement('section')
		toaster.setAttribute('data-sonner-toaster', '')
		const chrome = document.createElement('div')
		chrome.setAttribute('data-testid', 'page-chrome')
		document.body.append(portalHost, toaster, chrome)

		try {
			render(<OverlayHarness open onClose={vi.fn()} />)

			await waitFor(() => expect(chrome).toHaveAttribute('inert'))
			expect(portalHost).not.toHaveAttribute('inert')
			expect(toaster).not.toHaveAttribute('inert')
			// The subtree that contains the overlay must stay reachable.
			expect(screen.getByTestId('Overlay-dialog').closest('[inert]')).toBeNull()
		} finally {
			portalHost.remove()
			toaster.remove()
			chrome.remove()
		}
	})
})
