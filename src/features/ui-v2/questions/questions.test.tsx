import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { adaptQuestion } from '../../../adapters/ui-v2/from-backend'
import { mockQuestionDtos, mockQuestionsV2Empty, mockQuestionsV2Error } from '../../../mocks/ui-v2/questions-v2'
import { Uiv2QuestionCard, Uiv2QuestionsSection } from './QuestionsSection'

describe('adaptQuestion', () => {
	it('maps the canonical DTO with display-only answer reveal', () => {
		const [first, second] = mockQuestionDtos().map(adaptQuestion)
		expect(first).toMatchObject({
			id: 'mock-question-1',
			questionType: 'single_choice',
			difficulty: 'medium',
			source: 'backend',
		})
		expect(first.options).toHaveLength(3)
		expect(first.correctAnswer).toBe('B')
		expect(first.subjectLabel).toBeNull()
		// bare DTO degrades honestly
		expect(second.title).toBe('简述牛顿第二定律')
		expect(second.correctAnswer).toBeNull()
		expect(second.options).toEqual([])
	})
})

describe('Uiv2QuestionCard', () => {
	const [model] = mockQuestionDtos().map(adaptQuestion)

	it('browse -> answering -> result without ever judging correctness', () => {
		render(<Uiv2QuestionCard question={model} />)
		// answer hidden in browse state
		expect(screen.queryByText(/参考答案/)).not.toBeInTheDocument()

		fireEvent.click(screen.getByRole('button', { name: '开始作答' }))
		expect(screen.getByText('选择你的答案（本地练习，不评分）')).toBeInTheDocument()
		const reveal = screen.getByRole('button', { name: '查看解析' })
		expect(reveal).toBeDisabled()

		fireEvent.click(screen.getByLabelText('B. (-∞,-1),(1,+∞)'))
		expect(reveal).not.toBeDisabled()
		fireEvent.click(reveal)

		expect(screen.getByText('参考答案：B')).toBeInTheDocument()
		expect(screen.getByText(/解析：求导/)).toBeInTheDocument()
		// never claims 对/错
		expect(screen.queryByText(/回答正确/)).not.toBeInTheDocument()
		expect(screen.queryByText(/回答错误/)).not.toBeInTheDocument()
		expect(screen.getByText(/本地练习记录，不计入成绩/)).toBeInTheDocument()
	})

	it('handles questions without options or stored answers', () => {
		const [, bare] = mockQuestionDtos().map(adaptQuestion)
		render(<Uiv2QuestionCard question={bare} initialState="result" />)
		expect(screen.getByText('本题暂无收录答案')).toBeInTheDocument()
	})
})

describe('Uiv2QuestionsSection', () => {
	it('covers empty and error states', () => {
		const { rerender } = render(
			<Uiv2QuestionsSection
				model={{ state: 'empty', data: mockQuestionsV2Empty.data, error: null, source: 'mock' }}
			/>,
		)
		expect(screen.getByText('题库是空的，先去新建第一道题吧。')).toBeInTheDocument()

		rerender(
			<Uiv2QuestionsSection
				model={{ state: 'error', data: null, error: mockQuestionsV2Error.error, source: 'mock' }}
			/>,
		)
		expect(screen.getByRole('alert')).toHaveTextContent('mock: 题库加载失败，请重试')
	})
})
