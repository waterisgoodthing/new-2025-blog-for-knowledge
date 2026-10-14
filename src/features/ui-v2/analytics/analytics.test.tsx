import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import {
	mockAnalyticsAccumulating,
	mockAnalyticsEmpty,
	mockAnalyticsError,
	mockAnalyticsLoading,
	mockAnalyticsNormal,
} from '../../../mocks/ui-v2/analytics-v2'
import { Uiv2AnalyticsSection, Uiv2MasteryIndicator } from './AnalyticsSection'

describe('Uiv2MasteryIndicator', () => {
	it('renders an honest empty state for null values (no invented algorithm)', () => {
		render(<Uiv2MasteryIndicator mastery={{ value: null, confidence: 'low', source: 'mock' }} />)
		expect(screen.getByText('暂无足够数据，数据积累中')).toBeInTheDocument()
		expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
	})

	it('renders the value with a named progressbar when present', () => {
		render(<Uiv2MasteryIndicator mastery={{ value: 72, confidence: 'medium', source: 'backend' }} />)
		expect(screen.getByRole('progressbar', { name: '掌握度进度' })).toHaveAttribute(
			'aria-valuenow',
			'72',
		)
	})
})

describe('Uiv2AnalyticsSection', () => {
	it('renders all five data-backed blocks', () => {
		render(<Uiv2AnalyticsSection model={mockAnalyticsNormal} />)
		expect(screen.getByRole('heading', { name: '分析' })).toBeInTheDocument()
		expect(screen.getByText('掌握度')).toBeInTheDocument()
		expect(screen.getByText('复习完成情况')).toBeInTheDocument()
		expect(screen.getByText('学习趋势')).toBeInTheDocument()
		expect(screen.getByText('错题趋势')).toBeInTheDocument()
		expect(screen.getByText('薄弱点分布')).toBeInTheDocument()
	})

	it('renders the accumulating variant with honest copy everywhere', () => {
		render(<Uiv2AnalyticsSection model={mockAnalyticsAccumulating} />)
		expect(screen.getAllByText('暂无足够数据，数据积累中').length).toBeGreaterThanOrEqual(4)
	})

	it('covers loading / empty / error states', () => {
		const { rerender } = render(<Uiv2AnalyticsSection model={mockAnalyticsLoading} />)
		expect(screen.getByRole('status', { name: '正在加载学习分析' })).toBeInTheDocument()

		rerender(<Uiv2AnalyticsSection model={mockAnalyticsEmpty} />)
		expect(screen.getByText('还没有可分析的数据，先积累一些学习记录吧。')).toBeInTheDocument()

		rerender(<Uiv2AnalyticsSection model={mockAnalyticsError} />)
		expect(screen.getByRole('alert')).toHaveTextContent('mock: 学习分析加载失败，请重试')
	})
})
