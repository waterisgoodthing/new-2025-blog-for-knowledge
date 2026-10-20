import { useRef, useState } from 'react'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { resetOverlayState } from '@/hooks/use-overlay'
import { Uiv2Drawer } from './Drawer'
import { Uiv2Modal } from './Modal'

/**
 * jsdom cannot advance `motion`'s exit animation, so a dismissed overlay stays
 * mounted until the animation frame loop finishes (which never runs here).
 * Dismissal is therefore asserted at the component contract: the close callback
 * fired and focus was handed back. `open={false}` covers "renders nothing".
 */

beforeEach(() => {
	resetOverlayState()
})

afterEach(() => {
	resetOverlayState()
	vi.restoreAllMocks()
})

interface ModalCaseProps extends Partial<React.ComponentProps<typeof Uiv2Modal>> {
	initialOpen?: boolean
	onClosed?: () => void
}

function ModalCase({ initialOpen = false, onClosed, ...props }: ModalCaseProps) {
	const [open, setOpen] = useState(initialOpen)
	return (
		<>
			<button type='button' onClick={() => setOpen(true)}>
				open modal
			</button>
			<Uiv2Modal
				title='Confirm delete'
				description='This cannot be undone.'
				{...props}
				open={open}
				onClose={() => {
					setOpen(false)
					onClosed?.()
				}}
				footer={
					<button type='button' onClick={() => setOpen(false)}>
						confirm
					</button>
				}>
				<p>Body copy</p>
			</Uiv2Modal>
		</>
	)
}

describe('Uiv2Modal', () => {
	it('renders a named, described modal dialog', () => {
		render(<ModalCase initialOpen />)
		const dialog = screen.getByRole('dialog', { name: 'Confirm delete' })
		expect(dialog).toHaveAttribute('aria-modal', 'true')
		expect(dialog).toHaveAccessibleDescription('This cannot be undone.')
		expect(dialog).toHaveAttribute('data-testid', 'uiv2-modal')
	})

	it('applies the width presets', () => {
		const { rerender } = render(<ModalCase initialOpen size='confirm' />)
		expect(screen.getByTestId('uiv2-modal')).toHaveAttribute('data-size', 'confirm')
		expect(screen.getByTestId('uiv2-modal')).toHaveStyle({ maxWidth: '440px' })

		rerender(<ModalCase initialOpen size='form' />)
		expect(screen.getByTestId('uiv2-modal')).toHaveStyle({ maxWidth: '560px' })

		rerender(<ModalCase initialOpen size='preview' />)
		expect(screen.getByTestId('uiv2-modal')).toHaveStyle({ maxWidth: '720px' })
	})

	it('focuses the first interactive element and restores focus to the trigger on close', async () => {
		render(<ModalCase />)
		const trigger = screen.getByRole('button', { name: 'open modal' })
		trigger.focus()
		fireEvent.click(trigger)

		await waitFor(() => expect(screen.getByRole('button', { name: 'confirm' })).toHaveFocus())

		fireEvent.keyDown(document, { key: 'Escape' })
		await waitFor(() => expect(trigger).toHaveFocus())
	})

	it('honours an explicit initialFocusRef over the first body control', async () => {
		function WithInitialFocus() {
			const inputRef = useRef<HTMLInputElement>(null)
			return (
				<Uiv2Modal open onClose={vi.fn()} title='Focus target' initialFocusRef={inputRef as React.RefObject<HTMLElement | null>}>
					<button type='button'>body action</button>
					<input ref={inputRef} aria-label='preferred field' />
				</Uiv2Modal>
			)
		}
		render(<WithInitialFocus />)
		await waitFor(() => expect(screen.getByLabelText('preferred field')).toHaveFocus())
		expect(screen.getByRole('button', { name: 'body action' })).not.toHaveFocus()
	})

	it('dismisses on Escape', () => {
		const onClosed = vi.fn()
		render(<ModalCase initialOpen onClosed={onClosed} />)

		fireEvent.keyDown(document, { key: 'Escape' })
		expect(onClosed).toHaveBeenCalledTimes(1)
	})

	it('dismisses on a backdrop click', () => {
		const onClosed = vi.fn()
		render(<ModalCase initialOpen onClosed={onClosed} />)

		fireEvent.click(screen.getByTestId('uiv2-modal-backdrop'))
		expect(onClosed).toHaveBeenCalledTimes(1)
	})

	it('never dismisses from a click inside the dialog surface', () => {
		const onClosed = vi.fn()
		render(<ModalCase initialOpen onClosed={onClosed} />)

		fireEvent.click(screen.getByTestId('uiv2-modal'))
		expect(onClosed).not.toHaveBeenCalled()
	})

	it('honours closeOnBackdropClick=false', () => {
		const onClosed = vi.fn()
		render(<ModalCase initialOpen onClosed={onClosed} closeOnBackdropClick={false} />)

		fireEvent.click(screen.getByTestId('uiv2-modal-backdrop'))
		expect(onClosed).not.toHaveBeenCalled()
	})

	it('honours closeOnEscape=false', () => {
		const onClosed = vi.fn()
		render(<ModalCase initialOpen onClosed={onClosed} closeOnEscape={false} />)

		fireEvent.keyDown(document, { key: 'Escape' })
		expect(onClosed).not.toHaveBeenCalled()
	})

	it('wraps Tab at both ends of the dialog', async () => {
		render(<ModalCase initialOpen />)
		const confirm = screen.getByRole('button', { name: 'confirm' })
		const close = screen.getByRole('button', { name: '关闭' })
		await waitFor(() => expect(confirm).toHaveFocus())

		// forward wrap: last focusable (close) -> first (confirm)
		close.focus()
		fireEvent.keyDown(document, { key: 'Tab' })
		expect(confirm).toHaveFocus()

		// backward wrap: first (confirm) -> last (close)
		confirm.focus()
		fireEvent.keyDown(document, { key: 'Tab', shiftKey: true })
		expect(close).toHaveFocus()
	})

	it('renders nothing while closed', () => {
		render(<ModalCase />)
		expect(screen.queryByTestId('uiv2-modal')).not.toBeInTheDocument()
	})

	it('locks body scroll while open', async () => {
		render(<ModalCase initialOpen />)
		await waitFor(() => expect(document.body.style.overflow).toBe('hidden'))
	})
})

interface DrawerCaseProps extends Partial<React.ComponentProps<typeof Uiv2Drawer>> {
	initialOpen?: boolean
	onClosed?: () => void
}

function DrawerCase({ initialOpen = false, onClosed, ...props }: DrawerCaseProps) {
	const [open, setOpen] = useState(initialOpen)
	return (
		<>
			<button type='button' onClick={() => setOpen(true)}>
				open drawer
			</button>
			<Uiv2Drawer
				title='Filters'
				description='Refine the list'
				{...props}
				open={open}
				onClose={() => {
					setOpen(false)
					onClosed?.()
				}}
				footer={<button type='button'>apply</button>}>
				<button type='button'>first filter</button>
				<input aria-label='search' />
			</Uiv2Drawer>
		</>
	)
}

describe('Uiv2Drawer', () => {
	it.each(['left', 'right', 'bottom'] as const)('renders a %s drawer with header, body and footer', side => {
		render(<DrawerCase initialOpen side={side} />)
		const drawer = screen.getByRole('dialog', { name: 'Filters' })
		expect(drawer).toHaveAttribute('data-side', side)
		expect(drawer).toHaveAccessibleDescription('Refine the list')
		expect(screen.getByRole('button', { name: 'apply' })).toBeInTheDocument()
		expect(screen.getByRole('button', { name: 'first filter' })).toBeInTheDocument()
	})

	it('defaults to the right side', () => {
		render(<DrawerCase initialOpen />)
		expect(screen.getByRole('dialog')).toHaveAttribute('data-side', 'right')
	})

	it('sizes width for side drawers and height for the bottom sheet', () => {
		const { rerender } = render(<DrawerCase initialOpen side='right' size='440px' />)
		expect(screen.getByTestId('uiv2-drawer').getAttribute('style')).toContain('width: 440px')

		rerender(<DrawerCase initialOpen side='bottom' size='70vh' />)
		expect(screen.getByTestId('uiv2-drawer').getAttribute('style')).toContain('height: 70vh')
	})

	it('dismisses on Escape and restores focus to the trigger', async () => {
		const onClosed = vi.fn()
		render(<DrawerCase onClosed={onClosed} />)
		const trigger = screen.getByRole('button', { name: 'open drawer' })
		trigger.focus()
		fireEvent.click(trigger)

		await waitFor(() => expect(screen.getByRole('button', { name: 'first filter' })).toHaveFocus())

		fireEvent.keyDown(document, { key: 'Escape' })
		expect(onClosed).toHaveBeenCalledTimes(1)
		await waitFor(() => expect(trigger).toHaveFocus())
	})

	it('dismisses on backdrop click but not on inner clicks', () => {
		const onClosed = vi.fn()
		render(<DrawerCase initialOpen onClosed={onClosed} />)

		fireEvent.click(screen.getByTestId('uiv2-drawer'))
		expect(onClosed).not.toHaveBeenCalled()

		fireEvent.click(screen.getByTestId('uiv2-drawer-backdrop'))
		expect(onClosed).toHaveBeenCalledTimes(1)
	})

	it('exposes the reduced-motion flag for animation assertions', () => {
		render(<DrawerCase initialOpen />)
		expect(screen.getByTestId('uiv2-drawer')).toHaveAttribute('data-reduced-motion', 'false')
	})

	it('renders nothing while closed', () => {
		render(<DrawerCase />)
		expect(screen.queryByTestId('uiv2-drawer')).not.toBeInTheDocument()
	})
})

describe('Uiv2Modal stacked above Uiv2Drawer', () => {
	it('gives the modal a higher z-index than the drawer', async () => {
		render(
			<>
				<Uiv2Drawer open onClose={vi.fn()} title='Drawer'>
					<p>drawer body</p>
				</Uiv2Drawer>
				<Uiv2Modal open onClose={vi.fn()} title='Modal'>
					<p>modal body</p>
				</Uiv2Modal>
			</>
		)

		const drawer = screen.getByRole('dialog', { name: 'Drawer' })
		const modal = screen.getByRole('dialog', { name: 'Modal' })

		await waitFor(() => expect(Number(modal.style.zIndex)).toBeGreaterThan(Number(drawer.style.zIndex)))
	})
})

describe('Uiv2Modal — bare mode (legacy DialogModal parity)', () => {
	it('renders caller markup without a title header and names the dialog', () => {
		render(
			<Uiv2Modal open onClose={vi.fn()} bare ariaLabel='自定义对话框'>
				<p>legacy body</p>
			</Uiv2Modal>
		)

		const dialog = screen.getByRole('dialog', { name: '自定义对话框' })
		expect(dialog).toHaveAttribute('aria-modal', 'true')
		expect(screen.getByText('legacy body')).toBeInTheDocument()
		// No built-in header/close chrome is injected in bare mode.
		expect(screen.queryByRole('heading')).not.toBeInTheDocument()
		expect(screen.queryByRole('button', { name: '关闭' })).not.toBeInTheDocument()
	})

	it('keeps the overlay behaviours: Escape, backdrop policy and focus containment', async () => {
		const onClosed = vi.fn()
		render(
			<Uiv2Modal open onClose={onClosed} bare ariaLabel='bare' closeOnBackdropClick={false}>
				<button type='button'>inside</button>
			</Uiv2Modal>
		)

		await waitFor(() => expect(screen.getByRole('button', { name: 'inside' })).toHaveFocus())

		fireEvent.click(screen.getByTestId('uiv2-modal-backdrop'))
		expect(onClosed).not.toHaveBeenCalled()

		fireEvent.keyDown(document, { key: 'Escape' })
		expect(onClosed).toHaveBeenCalledTimes(1)
	})
})

describe('Uiv2Modal — naming and bare focus fallback', () => {
	it('falls back to aria-label when a non-bare dialog has no title', () => {
		render(
			<Uiv2Modal open onClose={vi.fn()} ariaLabel='无标题对话框'>
				<p>body</p>
			</Uiv2Modal>
		)
		const dialog = screen.getByRole('dialog', { name: '无标题对话框' })
		expect(dialog).not.toHaveAttribute('aria-labelledby')
		expect(screen.queryByRole('heading')).not.toBeInTheDocument()
	})

	it('closes bare dialogs on a backdrop click by default', () => {
		const onClosed = vi.fn()
		render(
			<Uiv2Modal open onClose={onClosed} bare ariaLabel='bare default'>
				<button type='button'>inside</button>
			</Uiv2Modal>
		)
		fireEvent.click(screen.getByTestId('uiv2-modal-backdrop'))
		expect(onClosed).toHaveBeenCalledTimes(1)
	})

	it('focuses the bare container when the content has no focusable child', async () => {
		render(
			<Uiv2Modal open onClose={vi.fn()} bare ariaLabel='no focusable'>
				<p>static comparison image</p>
			</Uiv2Modal>
		)
		await waitFor(() => expect(screen.getByRole('dialog', { name: 'no focusable' })).toHaveFocus())
	})
})
