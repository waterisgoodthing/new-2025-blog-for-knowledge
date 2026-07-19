import Link from 'next/link'
import {
  ArrowUpRight,
  CheckCircle2,
  CircleHelp,
  Clock3,
} from 'lucide-react'

import type { DashboardSummary } from '@/lib/api/dashboard'
import { formatChineseDateTime } from '@/lib/manage-display'
import { ManagePageHeader } from '../../components/manage-page-header'

type DashboardOverviewProps = {
  summary: DashboardSummary
}

type LearningFeedback = {
  title: string
  description: string
  href: string
  actionLabel: string
}

function displayTitle(title: string | null, questionText: string): string {
  return title?.trim() || questionText
}

export function getLearningFeedback(
  counts: Pick<DashboardSummary['counts'], 'due_reviews' | 'mistakes' | 'questions'>,
): LearningFeedback {
  if (counts.due_reviews > 0) {
    return {
      title: `完成 ${counts.due_reviews} 项到期复习`,
      description: '先完成今天到期的复习，再安排新的学习内容。',
      href: '/manage/review',
      actionLabel: '进入复习',
    }
  }

  if (counts.mistakes > 0) {
    return {
      title: `整理 ${counts.mistakes} 条已有错题`,
      description: '今天没有到期复习，可以从已有错题中继续整理学习记录。',
      href: '/manage/mistakes',
      actionLabel: '查看错题',
    }
  }

  if (counts.questions > 0) {
    return {
      title: '从已有题目开始复盘',
      description: '还没有错题记录，可从已有题目开始记录一次学习结果。',
      href: '/manage/questions',
      actionLabel: '查看题目',
    }
  }

  return {
    title: '从新建题目开始',
    description: '先添加一条题目，再逐步形成错题和复习记录。',
    href: '/manage/questions',
    actionLabel: '新建题目',
  }
}

const countItems = [
  { key: 'questions', label: '题目', href: '/manage/questions' },
  { key: 'mistakes', label: '错题', href: '/manage/mistakes' },
  { key: 'knowledge_points', label: '知识点', href: '/manage/knowledge-points' },
  { key: 'attachments', label: '附件', href: '/manage/attachments' },
] as const

export function DashboardOverview({ summary }: DashboardOverviewProps) {
  const latestMistake = summary.recent_mistakes[0]
  const storageReady = summary.system.storage === 'ok'
  const feedback = getLearningFeedback(summary.counts)

  return (
    <div className='space-y-10'>
      <ManagePageHeader
        eyebrow='学习空间'
        title='学习管理首页'
        description={`数据更新于 ${formatChineseDateTime(summary.generated_at)}`}
      />

      <section aria-labelledby='learning-feedback-title' className='border-y border-slate-200/70 py-5'>
        <p className='text-sm font-medium text-[var(--color-brand)]'>学习反馈</p>
        <div className='mt-2 flex flex-wrap items-end justify-between gap-4'>
          <div>
            <h2 id='learning-feedback-title' className='font-semibold text-slate-900'>{feedback.title}</h2>
            <p className='mt-1 text-sm text-slate-500'>{feedback.description}</p>
          </div>
          <Link
            href={feedback.href}
            className='inline-flex items-center gap-1 text-sm font-medium text-[var(--color-brand)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'
          >
            {feedback.actionLabel}
            <ArrowUpRight className='h-4 w-4' aria-hidden='true' />
          </Link>
        </div>
      </section>

      <section aria-labelledby='today-title'>
        <div className='flex items-end justify-between gap-4 border-b border-slate-200/70 pb-3'>
          <div>
            <h2 id='today-title' className='font-semibold text-slate-900'>今日任务</h2>
            <p className='mt-1 text-sm text-slate-500'>从待复习内容继续今天的学习。</p>
          </div>
          <Link
            href='/manage/review'
            className='inline-flex items-center gap-1 text-sm font-medium text-[var(--color-brand)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'
          >
            进入复习
            <ArrowUpRight className='h-4 w-4' aria-hidden='true' />
          </Link>
        </div>

        <div className='grid gap-0 md:grid-cols-2'>
          <Link
            href='/manage/review'
            className='group flex items-center justify-between gap-4 border-b border-slate-200/60 py-5 md:border-r md:pr-6'
          >
            <span>
              <span className='block text-sm text-slate-500'>待复习</span>
              <span className='mt-1 block text-3xl font-semibold tracking-tight text-slate-900'>
                {summary.counts.due_reviews}
              </span>
            </span>
            <Clock3 className='h-5 w-5 text-[var(--color-brand)]' aria-hidden='true' />
          </Link>

          <div className='flex min-w-0 items-center justify-between gap-4 border-b border-slate-200/60 py-5 md:pl-6'>
            <span className='min-w-0'>
              <span className='block text-sm text-slate-500'>最近错题</span>
              {latestMistake ? (
                <Link
                  href={`/manage/mistakes/${latestMistake.id}`}
                  className='mt-1 block truncate font-medium text-slate-800 hover:text-[var(--color-brand)]'
                >
                  {displayTitle(latestMistake.title, latestMistake.question_text)}
                </Link>
              ) : (
                <span className='mt-1 block text-sm text-slate-400'>暂无错题记录</span>
              )}
            </span>
            <ArrowUpRight className='h-4 w-4 shrink-0 text-slate-300' aria-hidden='true' />
          </div>
        </div>
      </section>

      <section aria-labelledby='content-counts-title'>
        <h2 id='content-counts-title' className='border-b border-slate-200/70 pb-3 font-semibold text-slate-900'>
          内容统计
        </h2>
        <div className='grid grid-cols-2 border-b border-slate-200/60 md:grid-cols-4'>
          {countItems.map((item, index) => (
            <Link
              key={item.key}
              href={item.href}
              className={`py-5 ${index % 2 === 0 ? 'border-r' : ''} border-slate-200/60 md:border-r md:px-5 md:first:pl-0 md:last:border-r-0`}
            >
              <span className='block text-sm text-slate-500'>{item.label}</span>
              <span className='mt-1 block text-2xl font-semibold tracking-tight text-slate-900'>
                {summary.counts[item.key]}
              </span>
            </Link>
          ))}
        </div>
      </section>

      <section aria-labelledby='recent-activity-title'>
        <h2 id='recent-activity-title' className='border-b border-slate-200/70 pb-3 font-semibold text-slate-900'>
          最近活动
        </h2>
        <div className='grid gap-8 pt-5 lg:grid-cols-2'>
          <div>
            <h3 className='text-sm font-medium text-slate-500'>最近题目</h3>
            <div className='mt-2 divide-y divide-slate-200/60'>
              {summary.recent_questions.length > 0 ? summary.recent_questions.map((question) => (
                <Link
                  key={question.id}
                  href={`/manage/questions/${question.id}`}
                  className='group flex items-center justify-between gap-4 py-3'
                >
                  <span className='min-w-0'>
                    <span className='block truncate text-sm font-medium text-slate-800 group-hover:text-[var(--color-brand)]'>
                      {displayTitle(question.title, question.question_text)}
                    </span>
                    <span className='mt-0.5 block text-xs text-slate-400'>{formatChineseDateTime(question.updated_at)}</span>
                  </span>
                  <ArrowUpRight className='h-4 w-4 shrink-0 text-slate-300' aria-hidden='true' />
                </Link>
              )) : (
                <p className='py-4 text-sm text-slate-400'>暂无题目</p>
              )}
            </div>
          </div>

          <div>
            <h3 className='text-sm font-medium text-slate-500'>最近复习</h3>
            <div className='mt-2 divide-y divide-slate-200/60'>
              {summary.recent_reviews.length > 0 ? summary.recent_reviews.map((review) => (
                <Link
                  key={review.id}
                  href='/manage/review'
                  className='group flex items-center justify-between gap-4 py-3'
                >
                  <span className='min-w-0'>
                    <span className='block truncate text-sm font-medium text-slate-800 group-hover:text-[var(--color-brand)]'>
                      {review.question_text}
                    </span>
                    <span className='mt-0.5 block text-xs text-slate-400'>
                      评分 {review.rating} · {formatChineseDateTime(review.reviewed_at)}
                    </span>
                  </span>
                  <ArrowUpRight className='h-4 w-4 shrink-0 text-slate-300' aria-hidden='true' />
                </Link>
              )) : (
                <p className='py-4 text-sm text-slate-400'>暂无复习记录</p>
              )}
            </div>
          </div>
        </div>
      </section>

      <section aria-labelledby='system-status-title'>
        <h2 id='system-status-title' className='border-b border-slate-200/70 pb-3 font-semibold text-slate-900'>
          系统状态
        </h2>
        <div className='flex flex-wrap gap-x-8 gap-y-3 pt-4 text-sm'>
          <span className='inline-flex items-center gap-2 text-emerald-700'>
            <CheckCircle2 className='h-4 w-4' aria-hidden='true' />服务正常
          </span>
          <span className='inline-flex items-center gap-2 text-emerald-700'>
            <CheckCircle2 className='h-4 w-4' aria-hidden='true' />数据库正常
          </span>
          <span className={`inline-flex items-center gap-2 ${storageReady ? 'text-emerald-700' : 'text-amber-700'}`}>
            {storageReady ? <CheckCircle2 className='h-4 w-4' aria-hidden='true' /> : <CircleHelp className='h-4 w-4' aria-hidden='true' />}
            {storageReady ? '附件存储正常' : '附件存储状态未知'}
          </span>
        </div>
      </section>
    </div>
  )
}
