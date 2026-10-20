import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { Uiv2Button } from './Button'

describe('Uiv2Button', () => {
	it('renders a button and forwards clicks', () => {
		const onClick = vi.fn()
		render(<Uiv2Button onClick={onClick}>保存</Uiv2Button>)

		const button = screen.getByRole('button', { name: '保存' })
		expect(button).toHaveAttribute('type', 'button')
		expect(button).toHaveAttribute('data-variant', 'primary')

		fireEvent.click(button)
		expect(onClick).toHaveBeenCalledTimes(1)
	})

	it('renders a link when href is provided', () => {
		render(
			<Uiv2Button href='/manage/review' ariaLabel='开始复习'>
				继续
			</Uiv2Button>
		)

		const link = screen.getByRole('link', { name: '开始复习' })
		expect(link).toHaveAttribute('href', '/manage/review')
		expect(link).toHaveAttribute('data-variant', 'primary')
		expect(screen.queryByRole('button')).not.toBeInTheDocument()
	})

	it('keeps the disabled button inert and never renders a link', () => {
		const onClick = vi.fn()
		render(
			<Uiv2Button href='/somewhere' disabled onClick={onClick}>
				不可用
			</Uiv2Button>
		)

		const button = screen.getByRole('button', { name: '不可用' })
		expect(button).toBeDisabled()
		fireEvent.click(button)
		expect(onClick).not.toHaveBeenCalled()
	})

	it('applies the ghost variant, extra classes and inline overrides', () => {
		render(
			<Uiv2Button variant='ghost' className='custom-class' style={{ minHeight: 32 }}>
				上一页
			</Uiv2Button>
		)

		const button = screen.getByRole('button', { name: '上一页' })
		expect(button).toHaveAttribute('data-variant', 'ghost')
		expect(button.className).toContain('uiv2-btn-ghost')
		expect(button.className).toContain('custom-class')
		expect(button).toHaveStyle({ minHeight: '32px' })
	})
})
