import { useRef } from 'react'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { resetOverlayState } from '@/hooks/use-overlay'
import {
	computeMenuPlacement,
	shouldUseNativeContextMenu,
	Uiv2ContextMenu,
	useContextMenuTrigger,
	type Uiv2ContextAction
} from './ContextMenu'

beforeEach(() => {
	resetOverlayState()
})

afterEach(() => {
	resetOverlayState()
	vi.restoreAllMocks()
})

function buildActions(overrides: Partial<Uiv2ContextAction>[] = []): Uiv2ContextAction[] {
	const base: Uiv2ContextAction[] = [
		{ id: 'open', label: '打开', group: 'open', run: vi.fn() },
		{ id: 'edit', label: '编辑', group: 'edit', run: vi.fn() },
		{ id: 'duplicate', label: '复制', group: 'edit', disabled: true, disabledReason: '没有权限', run: vi.fn() },
		{ id: 'delete', label: '删除', group: 'danger', variant: 'danger', run: vi.fn() }
	]
	return base.map((action, index) => ({ ...action, ...(overrides[index] ?? {}) }))
}

function MenuHarness({ actions = buildActions(), onClose = vi.fn() }: { actions?: Uiv2ContextAction[]; onClose?: () => void }) {
	return <Uiv2ContextMenu open onClose={onClose} actions={actions} position={{ x: 40, y: 60 }} />
}

describe('Uiv2ContextMenu — semantics', () => {
	it('renders a labelled menu with menuitems and a group separator', () => {
		render(<MenuHarness />)
		const menu = screen.getByRole('menu', { name: '对象操作' })
		expect(menu).toBeInTheDocument()
		expect(screen.getAllByRole('menuitem')).toHaveLength(4)
		expect(screen.getAllByRole('separator').length).toBeGreaterThan(0)
	})

	it('renders nothing while closed', () => {
		render(<Uiv2ContextMenu open={false} onClose={vi.fn()} actions={buildActions()} />)
		expect(screen.queryByRole('menu')).not.toBeInTheDocument()
	})

	it('positions at the pointer coordinates', () => {
		render(<MenuHarness />)
		const menu = screen.getByRole('menu')
		expect(menu.style.left).toBe('40px')
		expect(menu.style.top).toBe('60px')
	})

	it('buckets a danger variant into the danger group even without an explicit group', () => {
		render(
			<MenuHarness
				actions={[
					{ id: 'del', label: '删除', variant: 'danger', run: vi.fn() },
					{ id: 'open', label: '打开', run: vi.fn() }
				]}
			/>
		)
		const items = screen.getAllByRole('menuitem').map(item => item.textContent)
		expect(items).toEqual(['打开', '删除'])
		expect(screen.getAllByRole('separator').length).toBeGreaterThan(0)
	})

	it('marks disabled items and explains why', () => {
		render(<MenuHarness />)
		const duplicate = screen.getByRole('menuitem', { name: '复制' })
		expect(duplicate).toBeDisabled()
		expect(duplicate).toHaveAttribute('title', '没有权限')
	})
})

describe('Uiv2ContextMenu — keyboard', () => {
	it('focuses the first enabled item when opened', async () => {
		render(<MenuHarness />)
		await waitFor(() => expect(screen.getByRole('menuitem', { name: '打开' })).toHaveFocus())
	})

	it('moves with ArrowDown / ArrowUp and skips disabled items', async () => {
		render(<MenuHarness />)
		const open = screen.getByRole('menuitem', { name: '打开' })
		const edit = screen.getByRole('menuitem', { name: '编辑' })
		const remove = screen.getByRole('menuitem', { name: '删除' })

		await waitFor(() => expect(open).toHaveFocus())

		fireEvent.keyDown(open, { key: 'ArrowDown' })
		expect(edit).toHaveFocus()

		// "复制" is disabled, so the danger item is next and then it wraps.
		fireEvent.keyDown(edit, { key: 'ArrowDown' })
		expect(remove).toHaveFocus()

		fireEvent.keyDown(remove, { key: 'ArrowDown' })
		expect(open).toHaveFocus()

		fireEvent.keyDown(open, { key: 'ArrowUp' })
		expect(remove).toHaveFocus()
	})

	it('supports Home and End', async () => {
		render(<MenuHarness />)
		const open = screen.getByRole('menuitem', { name: '打开' })
		const remove = screen.getByRole('menuitem', { name: '删除' })
		await waitFor(() => expect(open).toHaveFocus())

		fireEvent.keyDown(open, { key: 'End' })
		expect(remove).toHaveFocus()

		fireEvent.keyDown(remove, { key: 'Home' })
		expect(open).toHaveFocus()
	})

	it('activates the focused item with Enter and closes first', async () => {
		const actions = buildActions()
		const onClose = vi.fn()
		render(<MenuHarness actions={actions} onClose={onClose} />)
		const open = screen.getByRole('menuitem', { name: '打开' })
		await waitFor(() => expect(open).toHaveFocus())

		fireEvent.keyDown(open, { key: 'Enter' })
		expect(onClose).toHaveBeenCalledTimes(1)
		expect(actions[0].run).toHaveBeenCalledTimes(1)
	})

	it('does not run a disabled item', async () => {
		const actions = buildActions()
		render(<MenuHarness actions={actions} />)
		fireEvent.click(screen.getByRole('menuitem', { name: '复制' }))
		expect(actions[2].run).not.toHaveBeenCalled()
	})

	it('closes on Escape', async () => {
		const onClose = vi.fn()
		render(<MenuHarness onClose={onClose} />)
		await waitFor(() => expect(screen.getByRole('menuitem', { name: '打开' })).toHaveFocus())

		fireEvent.keyDown(document, { key: 'Escape' })
		expect(onClose).toHaveBeenCalledTimes(1)
	})

	it('closes on an outside click', () => {
		const onClose = vi.fn()
		render(<MenuHarness onClose={onClose} />)
		fireEvent.click(screen.getByTestId('uiv2-context-menu-backdrop'))
		expect(onClose).toHaveBeenCalled()
	})
})

describe('computeMenuPlacement', () => {
	const viewport = { width: 1000, height: 800 }
	const menu = { width: 232, height: 200 }

	it('stays put when there is room', () => {
		expect(computeMenuPlacement({ x: 100, y: 100 }, menu, viewport)).toEqual({ x: 100, y: 100, flippedX: false, flippedY: false })
	})

	it('flips horizontally when it would overflow the right edge', () => {
		const result = computeMenuPlacement({ x: 900, y: 100 }, menu, viewport)
		expect(result.flippedX).toBe(true)
		expect(result.x).toBe(668)
	})

	it('flips vertically when it would overflow the bottom edge', () => {
		const result = computeMenuPlacement({ x: 100, y: 700 }, menu, viewport)
		expect(result.flippedY).toBe(true)
		expect(result.y).toBe(500)
	})

	it('clamps inside the viewport when both sides overflow', () => {
		const result = computeMenuPlacement({ x: 5, y: 5 }, { width: 1200, height: 900 }, viewport)
		expect(result.x).toBe(8)
		expect(result.y).toBe(8)
	})
})

describe('shouldUseNativeContextMenu', () => {
	it.each(['input', 'a', 'code', 'img', 'textarea'])('keeps the native menu on <%s>', tag => {
		const element = document.createElement(tag)
		if (tag === 'a') element.setAttribute('href', '/x')
		expect(shouldUseNativeContextMenu(element)).toBe(true)
	})

	it('allows a custom menu on a plain object surface', () => {
		const element = document.createElement('div')
		expect(shouldUseNativeContextMenu(element)).toBe(false)
	})

	it('keeps the native menu on a child of a protected element', () => {
		const link = document.createElement('a')
		link.setAttribute('href', '/x')
		const span = document.createElement('span')
		link.appendChild(span)
		expect(shouldUseNativeContextMenu(span)).toBe(true)
	})
})

function TriggerHarness({ disabled = false }: { disabled?: boolean }) {
	const actions = buildActions()
	const menu = useContextMenuTrigger({ actions, disabled })
	const surfaceRef = useRef<HTMLDivElement>(null)

	return (
		<div>
			<div ref={surfaceRef} data-testid='object' tabIndex={0} {...menu.triggerProps}>
				<span data-testid='object-text'>note card</span>
				<a href='/somewhere' data-testid='object-link'>
					link
				</a>
				<button type='button' {...menu.moreButtonProps} data-testid='more'>
					更多
				</button>
			</div>
			<Uiv2ContextMenu {...menu.menuProps} />
		</div>
	)
}

describe('useContextMenuTrigger', () => {
	it('opens on right-click at the pointer position', () => {
		render(<TriggerHarness />)
		fireEvent.contextMenu(screen.getByTestId('object-text'), { clientX: 120, clientY: 80 })

		const menu = screen.getByRole('menu')
		expect(menu.style.left).toBe('120px')
		expect(menu.style.top).toBe('80px')
	})

	it('opens on Shift+F10 and on the Menu key', () => {
		render(<TriggerHarness />)
		const object = screen.getByTestId('object')

		fireEvent.keyDown(object, { key: 'F10', shiftKey: true })
		expect(screen.getByRole('menu')).toBeInTheDocument()

		fireEvent.click(screen.getByTestId('uiv2-context-menu-backdrop'))
		fireEvent.keyDown(object, { key: 'ContextMenu' })
		expect(screen.getByRole('menu')).toBeInTheDocument()
	})

	it('opens from the visible more button and exposes menu state', () => {
		render(<TriggerHarness />)
		const more = screen.getByTestId('more')
		expect(more).toHaveAttribute('aria-haspopup', 'menu')
		expect(more).toHaveAttribute('aria-expanded', 'false')

		fireEvent.click(more)
		expect(screen.getByRole('menu')).toBeInTheDocument()
		expect(more).toHaveAttribute('aria-expanded', 'true')
	})

	it('does not hijack the native menu on links', () => {
		render(<TriggerHarness />)
		const link = screen.getByTestId('object-link')
		// fireEvent returns false when default was prevented.
		expect(fireEvent.contextMenu(link)).toBe(true)
		expect(screen.queryByRole('menu')).not.toBeInTheDocument()
	})

	it('stays closed when disabled', () => {
		render(<TriggerHarness disabled />)
		fireEvent.contextMenu(screen.getByTestId('object-text'))
		expect(screen.queryByRole('menu')).not.toBeInTheDocument()
	})
})

describe('focus restoration', () => {
	it('returns focus to the trigger after the menu closes', async () => {
		render(<TriggerHarness />)
		const object = screen.getByTestId('object')
		object.focus()
		fireEvent.contextMenu(object, { clientX: 10, clientY: 10 })

		await waitFor(() => expect(screen.getByRole('menu')).toBeInTheDocument())
		await waitFor(() => expect(screen.getByRole('menuitem', { name: '打开' })).toHaveFocus())

		fireEvent.keyDown(document, { key: 'Escape' })
		await waitFor(() => expect(object).toHaveFocus())
	})
})
