import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { adaptMistake } from '../../../adapters/ui-v2/from-backend'
import type { MistakeCardModel } from '../../../contracts/ui-v2/mistake'
import { mockMistakeDtos } from '../../../mocks/ui-v2/mistakes-v2'
import {
	applyMistakeFilter,
	Uiv2MistakeFilter,
	Uiv2MistakesSection,
} from './MistakesSection'
import { useMistakesModel } from './useMistakesModel'

const baseFilter = { status: 'all' as const, reason: 'all' as const, knowledgePointId: null, query: '' }

describe('adaptMistake', () => {
	it('maps the canonical DTO without inventing semantics', () => {
		const [first, second] = mockMistakeDtos().map(adaptMistake)
		expect(first).toMatchObject({
			id: 'mock-mistake-1',
			reasonCategory: 'concept',
			difficulty: 'medium',
			status: 'active',
			reviewItemId: 'mock-review-1',
			source: 'backend',
		})
		expect(first.subjectLabel).toBeNull()
		// null title falls back to question text; empty review_item_id -> null
		expect(second.title).toBe('牛顿第二定律应用：斜面加速度')
		expect(second.reviewItemId).toBeNull()
		expect(second.difficulty).toBe('unspecified')
	})
})

describe('applyMistakeFilter', () => {
	const models = mockMistakeDtos().map(adaptMistake)

	it('filters by status, reason, knowledge point and query', () => {
		expect(applyMistakeFilter(models, baseFilter)).toHaveLength(2)
		expect(
			applyMistakeFilter(models, { ...baseFilter, status: 'archived' }).map(m => m.id),
		).toEqual(['mock-mistake-2'])
		expect(
			applyMistakeFilter(models, { ...baseFilter, reason: 'concept' }).map(m => m.id),
		).toEqual(['mock-mistake-1'])
		expect(
			applyMistakeFilter(models, { ...baseFilter, knowledgePointId: 11 }).map(m => m.id),
		).toEqual(['mock-mistake-1'])
		expect(
			applyMistakeFilter(models, { ...baseFilter, query: '牛顿' }).map(m => m.id),
		).toEqual(['mock-mistake-2'])
	})
})

describe('Uiv2MistakesSection', () => {
	const models = mockMistakeDtos().map(adaptMistake)

	it('renders cards with review entry only when a review item exists', () => {
		render(
			<Uiv2MistakesSection
				model={{ state: 'ready', data: models, error: null, source: 'mock' }}
				filter={baseFilter}
				onFilterChange={() => {}}
			/>,
		)
		expect(screen.getByText('Mock：函数单调性区间求错')).toBeInTheDocument()
		expect(screen.getAllByRole('link', { name: '进入复习' })).toHaveLength(1)
		expect(screen.getByText('暂无复习安排')).toBeInTheDocument()
		// text-first status (not color-only); filter options share labels, so count both
		expect(screen.getAllByText('跟进中')).toHaveLength(2)
		expect(screen.getAllByText('已归档')).toHaveLength(2)
	})

	it('shows a no-match hint when the filter excludes everything', () => {
		render(
			<Uiv2MistakesSection
				model={{ state: 'ready', data: models, error: null, source: 'mock' }}
				filter={{ ...baseFilter, query: '不存在的内容' }}
				onFilterChange={() => {}}
			/>,
		)
		expect(screen.getByText('没有符合筛选条件的错题，换个条件试试。')).toBeInTheDocument()
	})

	it('filter controls are labelled and keyboard-operable', () => {
		const onChange = vi.fn()
		render(<Uiv2MistakeFilter filter={baseFilter} onChange={onChange} />)
		expect(screen.getByRole('form', { name: '错题筛选' })).toBeInTheDocument()
		fireEvent.change(screen.getByLabelText('状态'), { target: { value: 'active' } })
		expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ status: 'active' }))
		fireEvent.change(screen.getByLabelText('按标题或题干搜索错题'), { target: { value: '单调' } })
		expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ query: '单调' }))
	})
})

describe('useMistakesModel', () => {
	it('adapts DTOs and maps empty lists to the empty state', async () => {
		const fetchMistakes = vi.fn().mockResolvedValue(mockMistakeDtos())
		function Probe() {
			const { model } = useMistakesModel({ fetchMistakes })
			const first: MistakeCardModel | undefined = model.data?.[0]
			return <span data-testid="probe">{`${model.state}:${model.source}:${first?.id ?? 'none'}`}</span>
		}
		render(<Probe />)
		await waitFor(() =>
			expect(screen.getByTestId('probe')).toHaveTextContent('ready:backend:mock-mistake-1'),
		)

		fetchMistakes.mockResolvedValueOnce([])
		function EmptyProbe() {
			const { model, refresh } = useMistakesModel({ fetchMistakes, autoFetch: false })
			return (
				<div>
					<span data-testid="empty-state">{model.state}</span>
					<button type="button" onClick={() => void refresh()}>
						load
					</button>
				</div>
			)
		}
		render(<EmptyProbe />)
		screen.getByRole('button', { name: 'load' }).click()
		await waitFor(() => expect(screen.getByTestId('empty-state')).toHaveTextContent('empty'))
	})
})
