import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { adaptKnowledgeTree } from '../../../adapters/ui-v2/from-backend'
import {
	mockKnowledgeEmpty,
	mockKnowledgeError,
	mockKnowledgeLoading,
	mockKnowledgeNormal,
} from '../../../mocks/ui-v2/knowledge-v2'
import { Uiv2KnowledgeSection } from './KnowledgeSection'

describe('adaptKnowledgeTree', () => {
	it('maps structure while leaving learning signals unknown/null', () => {
		const node = adaptKnowledgeTree(
			{ id: 1, name: '数学' },
			[
				{
					id: 11,
					subject_id: 1,
					parent_id: null,
					name: '函数单调性',
					description: null,
					status: 'active',
					sort_order: 0,
					created_at: '',
					updated_at: '',
					children: [],
				},
			],
		)
		expect(node).toMatchObject({ id: 'subject-1', kind: 'subject', source: 'backend' })
		expect(node.children).toHaveLength(1)
		expect(node.children[0]).toMatchObject({
			id: 'kp-11',
			learningState: 'unknown',
			relatedQuestions: null,
			source: 'backend',
		})
	})
})

describe('Uiv2KnowledgeSection', () => {
	it('renders subjects with learning state and relation counters', () => {
		render(<Uiv2KnowledgeSection model={mockKnowledgeNormal} />)
		expect(screen.getByRole('heading', { name: '知识' })).toBeInTheDocument()
		expect(screen.getByText('函数单调性')).toBeInTheDocument()
		expect(screen.getByText('复习中')).toBeInTheDocument()
		// null counts render honestly
		expect(screen.getAllByText('数据积累中').length).toBeGreaterThan(0)
		expect(screen.getByText('题目：5 道')).toBeInTheDocument()
	})

	it('covers loading / empty / error states', () => {
		const { rerender } = render(<Uiv2KnowledgeSection model={mockKnowledgeLoading} />)
		expect(screen.getByRole('status', { name: '正在加载知识体系' })).toBeInTheDocument()

		rerender(<Uiv2KnowledgeSection model={mockKnowledgeEmpty} />)
		expect(screen.getByText('还没有科目，先去创建一个吧。')).toBeInTheDocument()

		rerender(<Uiv2KnowledgeSection model={mockKnowledgeError} />)
		expect(screen.getByRole('alert')).toHaveTextContent('mock: 知识体系加载失败，请重试')
	})
})
