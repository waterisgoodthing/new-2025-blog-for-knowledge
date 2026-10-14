import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { Uiv2Badge } from './Badge'
import { Uiv2Button } from './Button'
import { Uiv2Card } from './Card'
import { Uiv2ErrorState } from './ErrorState'
import { Uiv2Progress } from './Progress'
import { Uiv2Skeleton } from './Skeleton'

describe('ui-v2 presentational skeleton', () => {
	it('Progress with null renders 暂无足够数据 instead of a fabricated value', () => {
		render(<Uiv2Progress value={null} />)
		expect(screen.getByText('暂无足够数据')).toBeInTheDocument()
		expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
	})

	it('Progress with a value renders a bounded progressbar', () => {
		render(<Uiv2Progress value={150} />)
		expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '150')
	})

	it('ErrorState exposes text and an optional retry action', () => {
		const onRetry = vi.fn()
		const { rerender } = render(<Uiv2ErrorState message="加载失败" />)
		expect(screen.getByRole('alert')).toHaveTextContent('加载失败')
		expect(screen.queryByText('重试')).not.toBeInTheDocument()

		rerender(<Uiv2ErrorState message="加载失败" onRetry={onRetry} />)
		fireEvent.click(screen.getByText('重试'))
		expect(onRetry).toHaveBeenCalledTimes(1)
	})

	it('Skeleton renders the requested line count', () => {
		const { container } = render(<Uiv2Skeleton lines={4} />)
		expect(container.querySelectorAll('.uiv2-skeleton-line')).toHaveLength(4)
	})

	it('Badge exposes tone for styling without large color areas', () => {
		render(<Uiv2Badge text="错题" tone="mistake" />)
		expect(screen.getByText('错题')).toHaveAttribute('data-tone', 'mistake')
	})

	it('Button forwards clicks and disabled state', () => {
		const onClick = vi.fn()
		render(
			<Uiv2Card title="t">
				<Uiv2Button onClick={onClick}>去复习</Uiv2Button>
			</Uiv2Card>,
		)
		fireEvent.click(screen.getByText('去复习'))
		expect(onClick).toHaveBeenCalledTimes(1)
	})
})
