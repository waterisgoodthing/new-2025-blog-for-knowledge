import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { adaptTodayTasks } from '../../../adapters/ui-v2/from-backend'
import type { DashboardSummary } from '../../../lib/api/dashboard'
import type { ReviewPlan } from '../../../lib/api/review'
import {
	mockTodayEmpty,
	mockTodayError,
	mockTodayLoading,
	mockTodayNormal,
	mockTodayOverdue,
	mockTodayPartial,
} from '../../../mocks/ui-v2/today'
import { Uiv2StudyTaskCard, Uiv2TodaySection } from './TodaySection'

function summary(overrides: Partial<DashboardSummary> = {}): DashboardSummary {
	return {
		generated_at: '2026-09-15T00:00:00Z',
		counts: { questions: 10, mistakes: 4, knowledge_points: 6, attachments: 2, due_reviews: 3 },
		recent_questions: [],
		recent_mistakes: [
			{
				id: 'm1',
				title: null,
				question_text: '错题',
				reason_category: 'concept',
				updated_at: '2026-09-15',
			},
		],
		recent_reviews: [],
		sections: { learning: 'ready', activity: 'ready', storage: 'ok' },
		system: { service: 'ok', database: 'ok', storage: 'ok' },
		...overrides,
	}
}

const plan: ReviewPlan = {
	today_count: 3,
	overdue_count: 1,
	week_count: 8,
	next_review_date: null,
	subject_summaries: [],
	weaknesses: [],
	recommendations: [],
}

describe('adaptTodayTasks', () => {
	it('derives review + overdue + mistake tasks as estimated with provenance notes', () => {
		const tasks = adaptTodayTasks(summary(), plan)
		expect(tasks).toHaveLength(3)
		for (const task of tasks) {
			expect(task.source).toBe('estimated')
			expect(task.provenanceNote).toContain('GAP-001')
		}
		expect(tasks[0]).toMatchObject({ kind: 'review', status: 'pending', href: '/manage/review' })
		expect(tasks[1]).toMatchObject({ status: 'overdue' })
		expect(tasks[2]).toMatchObject({ kind: 'mistake_retry', href: '/manage/mistakes' })
	})

	it('never claims backend source and yields nothing when learning is unavailable', () => {
		const tasks = adaptTodayTasks(
			summary({ sections: { learning: 'unavailable', activity: 'ready', storage: 'ok' } }),
			null,
		)
		expect(tasks.some(t => t.source === 'backend')).toBe(false)
		expect(tasks.find(t => t.kind === 'review')).toBeUndefined()
	})
})

describe('Uiv2TodaySection', () => {
	it('renders tasks with kind/status badges and provenance notes', () => {
		render(<Uiv2TodaySection model={mockTodayNormal} />)
		expect(screen.getByRole('heading', { name: '今天学什么' })).toBeInTheDocument()
		expect(screen.getByText('Mock：复习 3 项到期错题')).toBeInTheDocument()
		expect(screen.getAllByText(/示例任务，非真实学习计划/).length).toBeGreaterThan(0)
		expect(screen.getAllByRole('link', { name: '进入学习任务' })).toHaveLength(3)
	})

	it('covers loading / empty / error / partial / overdue-filtered states', () => {
		const { rerender } = render(<Uiv2TodaySection model={mockTodayLoading} />)
		expect(screen.getByRole('status', { name: '正在加载今日任务' })).toBeInTheDocument()

		rerender(<Uiv2TodaySection model={mockTodayEmpty} />)
		expect(screen.getByText('今天没有安排。先去题库或复习页看看？')).toBeInTheDocument()

		rerender(<Uiv2TodaySection model={mockTodayError} />)
		expect(screen.getByRole('alert')).toHaveTextContent('mock: 今日任务加载失败，请重试')

		rerender(<Uiv2TodaySection model={mockTodayPartial} />)
		const notes = screen.getAllByRole('note')
		expect(notes[0]).toHaveTextContent('部分数据加载成功')

		rerender(<Uiv2TodaySection model={mockTodayOverdue} />)
		expect(screen.getByText('Mock：重做 2 道物理错题')).toBeInTheDocument()
		expect(screen.queryByText('Mock：复习 3 项到期错题')).not.toBeInTheDocument()
	})

	it('StudyTaskCard exposes overdue state in text, not color alone', () => {
		render(<Uiv2TodaySection model={mockTodayOverdue} />)
		expect(screen.getByText('已逾期')).toBeInTheDocument()
	})
})
