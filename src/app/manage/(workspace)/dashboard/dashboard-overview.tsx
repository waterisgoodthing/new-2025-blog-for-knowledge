import Link from 'next/link'
import {
  ArrowUpRight,
  Brain,
  CheckCircle2,
  CircleHelp,
  Clock3,
  FileText,
  Newspaper,
  ScanLine,
} from 'lucide-react'

import type { DashboardSummary } from '@/lib/api/dashboard'
import { normalizeHomePreferences, type AdminProfile, type HomeSection } from '@/lib/api/admin-profile'
import { formatChineseDateTime } from '@/lib/manage-display'
import { ManagePageHeader } from '../../components/manage-page-header'

type DashboardOverviewProps = {
  summary: DashboardSummary
  profile?: AdminProfile
  profileUnavailable?: boolean
  onProfileRetry?: () => void
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

export function getWelcomeGreeting(profile: Pick<AdminProfile, 'display_name' | 'timezone'>, now = new Date()): string {
  let hour = now.getHours()
  try {
    hour = Number(new Intl.DateTimeFormat('en-US', { hour: 'numeric', hourCycle: 'h23', timeZone: profile.timezone }).format(now))
  } catch {
    // Backend validates IANA zones; keep the UI usable if an old record is invalid.
  }
  const salutation = hour < 6 ? '夜深了' : hour < 12 ? '早上好' : hour < 18 ? '下午好' : '晚上好'
  return `${salutation}，${profile.display_name}`
}

function formatProfileTime(profile: Pick<AdminProfile, 'timezone'>, now = new Date()): string {
  try {
    return new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium', timeStyle: 'short', timeZone: profile.timezone }).format(now)
  } catch {
    return new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium', timeStyle: 'short' }).format(now)
  }
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

const quickActions = [
  {
    label: '写笔记',
    description: '记录知识与想法',
    href: '/write-note',
    icon: FileText,
    tone: 'border-blue-200/70 bg-blue-50/65 text-blue-700',
  },
  {
    label: '写博客',
    description: '整理并发布长文',
    href: '/write',
    icon: Newspaper,
    tone: 'border-emerald-200/70 bg-emerald-50/65 text-emerald-700',
  },
  {
    label: '图片采集',
    description: '识别并整理错题',
    href: '/manage/capture',
    icon: ScanLine,
    tone: 'border-amber-200/70 bg-amber-50/65 text-amber-700',
  },
  {
    label: '开始复习',
    description: '处理今天到期内容',
    href: '/manage/review',
    icon: Brain,
    tone: 'border-violet-200/70 bg-violet-50/65 text-violet-700',
  },
] as const

type DashboardSectionProps = { summary: DashboardSummary }

function QuickActionsSection() {
  return (
    <section aria-labelledby='quick-actions-title'>
      <div className='border-b border-slate-200/70 pb-3'>
        <h2 id='quick-actions-title' className='font-semibold text-slate-900'>快速开始</h2>
        <p className='mt-1 text-sm text-slate-500'>从现有、安全的流程继续今天的记录与学习。</p>
      </div>
      <div className='mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4'>
        {quickActions.map(({ label, description, href, icon: Icon, tone }) => (
          <Link
            key={href}
            href={href}
            aria-label={label}
            className={`group rounded-2xl border p-4 transition-[border-color,background-color,box-shadow] hover:shadow-sm motion-reduce:transition-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45 ${tone}`}
          >
            <span className='flex items-center justify-between gap-3'>
              <span className='font-medium'>{label}</span>
              <Icon className='h-4 w-4 shrink-0' aria-hidden='true' />
            </span>
            <span className='mt-2 block text-xs leading-5 text-slate-500'>{description}</span>
          </Link>
        ))}
      </div>
    </section>
  )
}

function TodaySection({ summary }: DashboardSectionProps) {
  const latestMistake = summary.recent_mistakes[0]
  const learningAvailable = summary.sections.learning !== 'unavailable'
  return <section data-dashboard-section='today' aria-labelledby='today-title'>
    <div className='flex items-end justify-between gap-4 border-b border-slate-200/70 pb-3'>
      <div><h2 id='today-title' className='font-semibold text-slate-900'>今日任务</h2><p className='mt-1 text-sm text-slate-500'>{learningAvailable ? '从待复习内容继续今天的学习。' : '今日摘要暂不可用；不会影响你从题库继续学习。'}</p></div>
      <Link href='/manage/review' className='inline-flex items-center gap-1 text-sm font-medium text-[var(--color-brand)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'>进入复习<ArrowUpRight className='h-4 w-4' aria-hidden='true' /></Link>
    </div>
    {learningAvailable ? <div className='grid gap-0 md:grid-cols-2'>
      <Link href='/manage/review' className='group flex items-center justify-between gap-4 border-b border-slate-200/60 py-5 md:border-r md:pr-6'><span><span className='block text-sm text-slate-500'>待复习</span><span className='mt-1 block text-3xl font-semibold tracking-tight text-slate-900'>{summary.counts.due_reviews}</span></span><Clock3 className='h-5 w-5 text-[var(--color-brand)]' aria-hidden='true' /></Link>
      <div className='flex min-w-0 items-center justify-between gap-4 border-b border-slate-200/60 py-5 md:pl-6'><span className='min-w-0'><span className='block text-sm text-slate-500'>最近错题</span>{latestMistake ? <Link href={`/manage/mistakes/${latestMistake.id}`} className='mt-1 block truncate font-medium text-slate-800 hover:text-[var(--color-brand)]'>{displayTitle(latestMistake.title, latestMistake.question_text)}</Link> : <span className='mt-1 block text-sm text-slate-400'>暂无错题记录</span>}</span><ArrowUpRight className='h-4 w-4 shrink-0 text-slate-300' aria-hidden='true' /></div>
    </div> : <p className='py-5 text-sm text-amber-700'>今日任务暂不可用</p>}
  </section>
}

function StatsSection({ summary }: DashboardSectionProps) {
  const learningAvailable = summary.sections.learning !== 'unavailable'
  return <section data-dashboard-section='stats' aria-labelledby='content-counts-title'>
    <h2 id='content-counts-title' className='border-b border-slate-200/70 pb-3 font-semibold text-slate-900'>内容统计</h2>
    {learningAvailable ? <div className='grid grid-cols-2 border-b border-slate-200/60 md:grid-cols-4'>{countItems.map((item, index) => <Link key={item.key} href={item.href} className={`py-5 ${index % 2 === 0 ? 'border-r' : ''} border-slate-200/60 md:border-r md:px-5 md:first:pl-0 md:last:border-r-0`}><span className='block text-sm text-slate-500'>{item.label}</span><span className='mt-1 block text-2xl font-semibold tracking-tight text-slate-900'>{summary.counts[item.key]}</span></Link>)}</div> : <p className='py-4 text-sm text-slate-500'>内容统计暂不可用</p>}
  </section>
}

function ActivitySection({ summary }: DashboardSectionProps) {
  const activityAvailable = summary.sections.activity !== 'unavailable'
  return <section data-dashboard-section='activity' aria-labelledby='recent-activity-title'>
    <h2 id='recent-activity-title' className='border-b border-slate-200/70 pb-3 font-semibold text-slate-900'>最近活动</h2>
    {activityAvailable ? <div className='grid gap-8 pt-5 lg:grid-cols-2'><div><h3 className='text-sm font-medium text-slate-500'>最近题目</h3><div className='mt-2 divide-y divide-slate-200/60'>{summary.recent_questions.length > 0 ? summary.recent_questions.map(question => <Link key={question.id} href={`/manage/questions/${question.id}`} className='group flex items-center justify-between gap-4 py-3'><span className='min-w-0'><span className='block truncate text-sm font-medium text-slate-800 group-hover:text-[var(--color-brand)]'>{displayTitle(question.title, question.question_text)}</span><span className='mt-0.5 block text-xs text-slate-400'>{formatChineseDateTime(question.updated_at)}</span></span><ArrowUpRight className='h-4 w-4 shrink-0 text-slate-300' aria-hidden='true' /></Link>) : <p className='py-4 text-sm text-slate-400'>暂无题目</p>}</div></div><div><h3 className='text-sm font-medium text-slate-500'>最近复习</h3><div className='mt-2 divide-y divide-slate-200/60'>{summary.recent_reviews.length > 0 ? summary.recent_reviews.map(review => <Link key={review.id} href='/manage/review' className='group flex items-center justify-between gap-4 py-3'><span className='min-w-0'><span className='block truncate text-sm font-medium text-slate-800 group-hover:text-[var(--color-brand)]'>{review.question_text}</span><span className='mt-0.5 block text-xs text-slate-400'>评分 {review.rating} · {formatChineseDateTime(review.reviewed_at)}</span></span><ArrowUpRight className='h-4 w-4 shrink-0 text-slate-300' aria-hidden='true' /></Link>) : <p className='py-4 text-sm text-slate-400'>暂无复习记录</p>}</div></div></div> : <p className='pt-4 text-sm text-slate-500'>最近活动暂不可用</p>}
  </section>
}

function StorageSection({ summary }: DashboardSectionProps) {
  const storageHealthy = summary.sections.storage !== 'unknown' && summary.system.storage === 'ok'
  return <section data-dashboard-section='storage' aria-labelledby='system-status-title'>
    <h2 id='system-status-title' className='border-b border-slate-200/70 pb-3 font-semibold text-slate-900'>系统状态</h2>
    <div className='flex flex-wrap gap-x-8 gap-y-3 pt-4 text-sm'><span className='inline-flex items-center gap-2 text-emerald-700'><CheckCircle2 className='h-4 w-4' aria-hidden='true' />服务正常</span><span className={`inline-flex items-center gap-2 ${summary.system.database === 'ok' ? 'text-emerald-700' : 'text-amber-700'}`}>{summary.system.database === 'ok' ? <CheckCircle2 className='h-4 w-4' aria-hidden='true' /> : <CircleHelp className='h-4 w-4' aria-hidden='true' />}{summary.system.database === 'ok' ? '数据库正常' : '数据库状态未知'}</span><span className={`inline-flex items-center gap-2 ${storageHealthy ? 'text-emerald-700' : 'text-amber-700'}`}>{storageHealthy ? <CheckCircle2 className='h-4 w-4' aria-hidden='true' /> : <CircleHelp className='h-4 w-4' aria-hidden='true' />}{summary.sections.storage === 'empty' ? '暂无附件' : storageHealthy ? '附件存储正常' : '附件存储状态未知'}</span></div>
  </section>
}

function renderDashboardSection(section: HomeSection, summary: DashboardSummary) {
  if (section === 'today') return <TodaySection key={section} summary={summary} />
  if (section === 'activity') return <ActivitySection key={section} summary={summary} />
  if (section === 'stats') return <StatsSection key={section} summary={summary} />
  return <StorageSection key={section} summary={summary} />
}

export function DashboardOverview({ summary, profile, profileUnavailable = false, onProfileRetry }: DashboardOverviewProps) {
  const preferences = normalizeHomePreferences(profile?.home_preferences)
  const visibleSections = preferences.section_order.filter(section => !preferences.hidden_sections.includes(section))
  const learningAvailable = summary.sections.learning !== 'unavailable'
  const feedback = learningAvailable ? getLearningFeedback(summary.counts) : { title: '学习摘要暂不可用', description: '可以先从题目开始继续学习，稍后再刷新查看今日安排。', href: '/manage/questions', actionLabel: '新建题目' }

  return <div className='space-y-10'>
    {profile ? (profile.home_preferences.show_welcome ? <section aria-labelledby='private-welcome-title' className='rounded-2xl border border-[var(--color-brand)]/15 bg-[var(--color-brand)]/5 px-5 py-4'><p className='text-xs font-medium tracking-[0.12em] text-[var(--color-brand)] uppercase'>个人学习</p><h2 id='private-welcome-title' className='mt-2 text-xl font-semibold text-slate-900'>{getWelcomeGreeting(profile)}</h2><p className='mt-1 text-sm text-slate-600'>{profile.welcome_message || profile.signature || '按自己的节奏继续积累。'}</p><p className='mt-2 text-xs text-slate-400'>当前时间：{formatProfileTime(profile)}</p></section> : null) : profileUnavailable ? <section aria-labelledby='private-welcome-unavailable-title' className='rounded-2xl border border-amber-200 bg-amber-50/70 px-5 py-4'><h2 id='private-welcome-unavailable-title' className='font-semibold text-amber-900'>个人资料暂不可用</h2><p className='mt-1 text-sm text-amber-800'>学习摘要仍可使用；稍后可重试加载私有欢迎区域。</p>{onProfileRetry ? <button type='button' onClick={onProfileRetry} className='mt-3 text-sm font-medium text-amber-900 underline underline-offset-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-700/40'>重新加载个人资料</button> : null}</section> : null}
    <ManagePageHeader eyebrow='学习空间' title='学习管理首页' description={`数据更新于 ${formatChineseDateTime(summary.generated_at)}`} />
    <QuickActionsSection />
    <section aria-labelledby='learning-feedback-title' className='border-y border-slate-200/70 py-5'><p className='text-sm font-medium text-[var(--color-brand)]'>学习反馈</p><div className='mt-2 flex flex-wrap items-end justify-between gap-4'><div><h2 id='learning-feedback-title' className='font-semibold text-slate-900'>{feedback.title}</h2><p className='mt-1 text-sm text-slate-500'>{feedback.description}</p></div><Link href={feedback.href} className='inline-flex items-center gap-1 text-sm font-medium text-[var(--color-brand)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'>{feedback.actionLabel}<ArrowUpRight className='h-4 w-4' aria-hidden='true' /></Link></div></section>
    <div className='space-y-10'>{visibleSections.map(section => renderDashboardSection(section, summary))}</div>
  </div>
}
