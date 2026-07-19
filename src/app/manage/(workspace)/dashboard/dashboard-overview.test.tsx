import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import type { DashboardSummary } from '@/lib/api/dashboard'
import { DashboardOverview, getLearningFeedback } from './dashboard-overview'

const summary: DashboardSummary = {
  generated_at: '2026-07-19T10:00:00Z',
  counts: {
    questions: 12,
    mistakes: 5,
    knowledge_points: 8,
    attachments: 3,
    due_reviews: 2,
  },
  recent_questions: [
    {
      id: 'question-1',
      title: '极限练习',
      question_text: '求这个函数的极限',
      updated_at: '2026-07-19T09:00:00Z',
    },
  ],
  recent_mistakes: [
    {
      id: 'mistake-1',
      title: null,
      question_text: '链表删除节点',
      reason_category: 'concept',
      updated_at: '2026-07-19T08:00:00Z',
    },
  ],
  recent_reviews: [
    {
      id: 'review-1',
      review_item_id: 'item-1',
      rating: 4,
      reviewed_at: '2026-07-19T07:00:00Z',
      question_text: '概率计算',
    },
  ],
  system: {
    service: 'ok',
    database: 'ok',
    storage: 'ok',
  },
}

describe('DashboardOverview', () => {
  it('shows real learning counts, current work and recent activity in Chinese', () => {
    render(<DashboardOverview summary={summary} />)

    expect(screen.getByRole('heading', { name: '学习管理首页' })).toBeInTheDocument()
    expect(screen.getByText('待复习')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('题目')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByText('最近题目')).toBeInTheDocument()
    expect(screen.getByText('极限练习')).toBeInTheDocument()
    expect(screen.getByText('最近复习')).toBeInTheDocument()
    expect(screen.getByText('概率计算')).toBeInTheDocument()
    expect(screen.getByText('服务正常')).toBeInTheDocument()
    expect(screen.queryByText(/Coming Soon|No API connected|Static shell/i)).not.toBeInTheDocument()
  })

  it.each([
    [{ due_reviews: 2, mistakes: 5, questions: 12 }, '完成 2 项到期复习', '/manage/review'],
    [{ due_reviews: 0, mistakes: 5, questions: 12 }, '整理 5 条已有错题', '/manage/mistakes'],
    [{ due_reviews: 0, mistakes: 0, questions: 12 }, '从已有题目开始复盘', '/manage/questions'],
    [{ due_reviews: 0, mistakes: 0, questions: 0 }, '从新建题目开始', '/manage/questions'],
  ] as const)('derives deterministic learning feedback for the current summary', (counts, title, href) => {
    expect(getLearningFeedback(counts)).toMatchObject({ title, href })
  })
})
