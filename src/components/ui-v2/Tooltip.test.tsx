import { act, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { Uiv2Tooltip } from './Tooltip'

beforeEach(() => {
	vi.useFakeTimers()
})

afterEach(() => {
	vi.useRealTimers()
	vi.restoreAllMocks()
})

describe('Uiv2Tooltip', () => {
	it('renders the trigger immediately and the tooltip only after the delay', () => {
		render(
			<Uiv2Tooltip content='插入模板到光标位置'>
				<button type='button'>模板</button>
			</Uiv2Tooltip>
		)

		const trigger = screen.getByRole('button', { name: '模板' })
		expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()

		fireEvent.mouseEnter(trigger.parentElement as HTMLElement)
		act(() => {
			vi.advanceTimersByTime(599)
		})
		expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()

		act(() => {
			vi.advanceTimersByTime(1)
		})
		expect(screen.getByRole('tooltip')).toHaveTextContent('插入模板到光标位置')
	})

	it('hides the tooltip on mouse leave and cancels a pending reveal', () => {
		render(
			<Uiv2Tooltip content='加粗'>
				<button type='button'>B</button>
			</Uiv2Tooltip>
		)
		const wrapper = screen.getByRole('button', { name: 'B' }).parentElement as HTMLElement

		fireEvent.mouseEnter(wrapper)
		fireEvent.mouseLeave(wrapper)
		act(() => {
			vi.advanceTimersByTime(1000)
		})
		expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()

		fireEvent.mouseEnter(wrapper)
		act(() => {
			vi.advanceTimersByTime(600)
		})
		expect(screen.getByRole('tooltip')).toBeInTheDocument()

		fireEvent.mouseLeave(wrapper)
		expect(screen.queryByRole('tooltip')).not.toBeInTheDocument()
	})

	it('honours a custom delay', () => {
		render(
			<Uiv2Tooltip content='提示' delay={200}>
				<button type='button'>X</button>
			</Uiv2Tooltip>
		)
		const wrapper = screen.getByRole('button', { name: 'X' }).parentElement as HTMLElement

		fireEvent.mouseEnter(wrapper)
		act(() => {
			vi.advanceTimersByTime(200)
		})
		expect(screen.getByRole('tooltip')).toBeInTheDocument()
	})
})
