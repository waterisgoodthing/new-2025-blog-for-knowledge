import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import type { DashboardSummary } from '@/lib/api/dashboard'
import { DashboardOverview, getLearningFeedback, getWelcomeGreeting } from './dashboard-overview'

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
  sections: {
    learning: 'ready',
    activity: 'ready',
    storage: 'ready',
  },
  system: {
    service: 'ok',
    database: 'ok',
    storage: 'ok',
  },
}

describe('DashboardOverview', () => {
  it('uses the private timezone for the administrator welcome area', () => {
    expect(getWelcomeGreeting({ display_name: 'I5 Owner', timezone: 'UTC' }, new Date('2026-07-22T08:00:00Z'))).toBe('早上好，I5 Owner')
  })

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

  it('offers real daily actions without creating a parallel workspace route', () => {
    render(<DashboardOverview summary={summary} />)

    expect(screen.getByRole('heading', { name: '快速开始' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: '写笔记' })).toHaveAttribute('href', '/write-note')
    expect(screen.getByRole('link', { name: '写博客' })).toHaveAttribute('href', '/write')
    expect(screen.getByRole('link', { name: '图片采集' })).toHaveAttribute('href', '/manage/capture')
    expect(screen.getByRole('link', { name: '开始复习' })).toHaveAttribute('href', '/manage/review')

    const hrefs = screen.getAllByRole('link').map(link => link.getAttribute('href'))
    expect(hrefs.some(href => href?.startsWith('/workspace'))).toBe(false)
  })

  it('renders dashboard sections in preference order and omits hidden sections', () => {
    render(
      <DashboardOverview
        summary={summary}
        profile={{
          id: 'profile-1',
          user_id: 'user-1',
          display_name: 'I5 Owner',
          identity_title: 'Learner',
          signature: '',
          welcome_message: '',
          timezone: 'UTC',
          home_preferences: {
            show_welcome: false,
            section_order: ['activity', 'today', 'storage', 'stats'],
            hidden_sections: ['stats'],
          },
        }}
      />,
    )

    const headings = Array.from(document.querySelectorAll('section[data-dashboard-section] h2')).map(node => node.textContent)
    expect(headings).toEqual(['最近活动', '今日任务', '系统状态'])
    expect(screen.queryByRole('heading', { name: '内容统计' })).not.toBeInTheDocument()
  })

  it.each([
    [{ due_reviews: 2, mistakes: 5, questions: 12 }, '完成 2 项到期复习', '/manage/review'],
    [{ due_reviews: 0, mistakes: 5, questions: 12 }, '整理 5 条已有错题', '/manage/mistakes'],
    [{ due_reviews: 0, mistakes: 0, questions: 12 }, '从已有题目开始复盘', '/manage/questions'],
    [{ due_reviews: 0, mistakes: 0, questions: 0 }, '从新建题目开始', '/manage/questions'],
  ] as const)('derives deterministic learning feedback for the current summary', (counts, title, href) => {
    expect(getLearningFeedback(counts)).toMatchObject({ title, href })
  })

  it('keeps a safe learning action while the today-summary section is unavailable', () => {
    const unavailableSummary = {
      ...summary,
          sections: { learning: 'unavailable', activity: 'ready', storage: 'ready' },
      system: { ...summary.system, database: 'unavailable' },
    } as unknown as DashboardSummary

    render(
      <DashboardOverview summary={unavailableSummary} />,
    )

    expect(screen.getByText('今日任务暂不可用')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: '新建题目' })).toHaveAttribute('href', '/manage/questions')
    expect(screen.getByText('数据库状态未知')).toBeInTheDocument()
  })

  it('shows independent activity failure and unknown storage without hiding learning', () => {
    const partialSummary = {
      ...summary,
      sections: { learning: 'ready', activity: 'unavailable', storage: 'unknown' },
      system: { ...summary.system, storage: 'unknown' },
    } as DashboardSummary

    render(<DashboardOverview summary={partialSummary} />)

    expect(screen.getByText('最近活动暂不可用')).toBeInTheDocument()
    expect(screen.getByText('附件存储状态未知')).toBeInTheDocument()
    expect(screen.getByText('待复习')).toBeInTheDocument()
  })

  it('treats empty storage as healthy while showing the empty label', () => {
    render(<DashboardOverview summary={{
      ...summary,
      sections: { ...summary.sections, storage: 'empty' },
      system: { ...summary.system, storage: 'ok' },
    }} />)

    expect(screen.getByText('暂无附件')).toBeInTheDocument()
    expect(screen.getByText('服务正常')).toBeInTheDocument()
  })

  it('keeps the I4 dashboard usable when private profile data is unavailable', () => {
    const retry = vi.fn()
    render(<DashboardOverview summary={summary} profileUnavailable onProfileRetry={retry} />)

    expect(screen.getByRole('heading', { name: '个人资料暂不可用' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '重新加载个人资料' }))
    expect(retry).toHaveBeenCalledOnce()
    expect(screen.getByText('待复习')).toBeInTheDocument()
  })
})
