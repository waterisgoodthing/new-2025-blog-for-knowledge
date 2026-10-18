import Link from 'next/link'
import { ArrowUpRight, Award, Brain, CheckCircle2, CircleHelp, Clock3, FileText, Newspaper, PencilLine, ScanLine, TrendingDown } from 'lucide-react'

import type {
	DashboardRecentlyMasteredItem,
	DashboardSectionAction,
	DashboardSummary,
	DashboardTodayFirstAction,
	DashboardWeakKnowledgePoint
} from '@/lib/api/dashboard'
import { normalizeHomePreferences, type AdminProfile, type HomeSection } from '@/lib/api/admin-profile'
import { formatChineseDateTime } from '@/lib/manage-display'
import { AsyncStatePanel } from '@/components/async-state-panel'
import { Uiv2Badge, Uiv2Button, Uiv2Card, Uiv2PageHeader } from '@/components/ui-v2'

type DashboardOverviewProps = {
	summary: DashboardSummary
	profile?: AdminProfile
	profileError?: unknown
	profileLoading?: boolean
	profileUnavailable?: boolean
	onProfileRetry?: () => void
	onSummaryRetry?: () => void
}

const FIRST_ACTION_REASON_TEXT: Record<string, string> = {
	due_reviews_first: '今天有到期复习，先完成它们再安排练习。',
	practice_first_no_due_reviews: '今天没有到期复习，先用薄弱知识点练习。',
	nothing_scheduled: '今天没有到期复习，也没有可练习题目。'
}

export function firstActionReasonText(reason: string): string {
	return FIRST_ACTION_REASON_TEXT[reason] ?? '按确定性优先级安排今天的学习。'
}

function firstActionTitle(action: DashboardTodayFirstAction): string {
	if (action.kind === 'practice') return `完成 ${action.count} 道今日练习`
	return `完成 ${action.count} 项到期复习`
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

const countItems = [
	{ key: 'questions', label: '题目', href: '/manage/questions' },
	{ key: 'mistakes', label: '错题', href: '/manage/mistakes' },
	{ key: 'knowledge_points', label: '知识点', href: '/manage/knowledge-points' },
	{ key: 'attachments', label: '附件', href: '/manage/attachments' }
] as const

const quickActions = [
	{
		label: '写笔记',
		description: '记录知识与想法',
		href: '/manage/notes/new?type=note',
		icon: FileText,
		tone: 'border-blue-200/70 bg-blue-50/65 text-blue-700'
	},
	{
		label: '写博客',
		description: '整理并发布长文',
		href: '/manage/notes/new?type=blog',
		icon: Newspaper,
		tone: 'border-emerald-200/70 bg-emerald-50/65 text-emerald-700'
	},
	{
		label: '图片采集',
		description: '识别并整理错题',
		href: '/manage/capture',
		icon: ScanLine,
		tone: 'border-amber-200/70 bg-amber-50/65 text-amber-700'
	},
	{
		label: '开始复习',
		description: '处理今天到期内容',
		href: '/manage/review',
		icon: Brain,
		tone: 'border-violet-200/70 bg-violet-50/65 text-violet-700'
	}
] as const

type DashboardSectionProps = { summary: DashboardSummary; onRetry?: () => void }

function QuickActionsSection() {
	return (
		<section aria-labelledby='quick-actions-title'>
			<div className='border-b border-[var(--admin-border)] pb-3'>
				<h2 id='quick-actions-title' className='font-semibold text-[var(--admin-text-primary)]'>
					快速开始
				</h2>
				<p className='mt-1 text-sm text-[var(--admin-text-secondary)]'>从现有、安全的流程继续今天的记录与学习。</p>
			</div>
			<div className='mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4'>
				{quickActions.map(({ label, description, href, icon: Icon, tone }) => (
					<Link
						key={href}
						href={href}
						aria-label={label}
						className={`group rounded-2xl border p-4 transition-[border-color,background-color,box-shadow] hover:shadow-sm focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45 focus-visible:outline-none motion-reduce:transition-none ${tone}`}>
						<span className='flex items-center justify-between gap-3'>
							<span className='font-medium'>{label}</span>
							<Icon className='h-4 w-4 shrink-0' aria-hidden='true' />
						</span>
						<span className='mt-2 block text-xs leading-5 text-[var(--admin-text-secondary)]'>{description}</span>
					</Link>
				))}
			</div>
		</section>
	)
}

type AsyncStateAction = () => void

export function TodayFirstActionBanner({
	action,
	unavailable,
	onRetry
}: {
	action: DashboardTodayFirstAction
	unavailable: boolean
	onRetry?: AsyncStateAction
}) {
	if (unavailable) {
		return (
			<section aria-labelledby='today-first-action-title' className='border-y border-[var(--admin-border)] py-5'>
				<p className='text-sm font-medium text-[var(--color-brand)]'>今日先做</p>
				<AsyncStatePanel
					status='error'
					title='今日安排暂不可用'
					error='复习与练习数据都未能加载，请稍后重试。'
					onRetry={onRetry}
					retryLabel='重新尝试'
				/>
				<h2 id='today-first-action-title' className='sr-only'>
					今日先做
				</h2>
			</section>
		)
	}

	if (action.kind === 'none' || !action.target_route) {
		return (
			<section aria-labelledby='today-first-action-title' className='border-y border-[var(--admin-border)] py-5'>
				<p className='text-sm font-medium text-[var(--color-brand)]'>今日先做</p>
				<AsyncStatePanel status='empty' title='今天没有安排' emptyHint='当前没有到期复习，也没有可练习题目；可以从题库自由学习。' />
				<h2 id='today-first-action-title' className='sr-only'>
					今日先做
				</h2>
			</section>
		)
	}

	return (
		<section aria-labelledby='today-first-action-title' className='rounded-2xl border border-[var(--color-brand)]/20 bg-[var(--color-brand)]/5 px-5 py-6'>
			<p className='text-xs font-medium tracking-[0.12em] text-[var(--color-brand)] uppercase'>今日先做</p>
			<div className='mt-3 flex flex-wrap items-end justify-between gap-4'>
				<div>
					<h2 id='today-first-action-title' className='text-xl font-semibold text-[var(--admin-text-primary)]'>
						{firstActionTitle(action)}
					</h2>
					<p className='mt-1 text-sm text-[var(--admin-text-secondary)]'>{firstActionReasonText(action.reason)}</p>
				</div>
				<Uiv2Button
					href={action.target_route}
					ariaLabel={action.kind === 'practice' ? '今日先做：开始练习' : '今日先做：开始复习'}
					className='gap-1 rounded-lg text-sm font-semibold'
					style={{ minHeight: 44, paddingLeft: 16, paddingRight: 16 }}>
					{action.kind === 'practice' ? '开始练习' : '开始复习'}
					<ArrowUpRight className='h-4 w-4' aria-hidden='true' />
				</Uiv2Button>
			</div>
		</section>
	)
}

function ReviewTodayPanel({
	action,
	count,
	available,
	onRetry
}: {
	action: DashboardSectionAction
	count: number
	available: boolean
	onRetry?: AsyncStateAction
}) {
	if (!available || !action.available) {
		return <AsyncStatePanel status='error' title='复习数据暂不可用' error='稍后重试后即可看到今天的到期复习。' onRetry={onRetry} retryLabel='重新尝试' />
	}
	if (count === 0) {
		return <AsyncStatePanel status='empty' title='今日无到期复习' emptyHint='当前没有需要复习的内容。' />
	}
	return (
		<Uiv2Card>
			<div className='flex items-center justify-between gap-3'>
				<p className='text-sm font-medium text-[var(--admin-text-secondary)]'>今日复习</p>
				<Clock3 className='h-4 w-4 text-[var(--color-brand)]' aria-hidden='true' />
			</div>
			<p className='mt-2 text-3xl font-semibold tracking-tight text-[var(--admin-text-primary)]'>{count}</p>
			<Link
				href={action.target_route}
				className='mt-3 inline-flex items-center gap-1 text-sm font-medium text-[var(--color-brand)] focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45 focus-visible:outline-none'>
				进入复习
				<ArrowUpRight className='h-4 w-4' aria-hidden='true' />
			</Link>
		</Uiv2Card>
	)
}

function PracticeTodayPanel({
	action,
	count,
	available,
	onRetry
}: {
	action: DashboardSectionAction
	count: number
	available: boolean
	onRetry?: AsyncStateAction
}) {
	if (!available || !action.available) {
		return <AsyncStatePanel status='error' title='练习数据暂不可用' error='稍后重试后即可看到今天的练习安排。' onRetry={onRetry} retryLabel='重新尝试' />
	}
	if (count === 0) {
		return <AsyncStatePanel status='empty' title='今日暂无合适练习' emptyHint='当前没有符合薄弱知识点条件的练习题目。' />
	}
	return (
		<Uiv2Card>
			<div className='flex items-center justify-between gap-3'>
				<p className='text-sm font-medium text-[var(--admin-text-secondary)]'>今日练习</p>
				<PencilLine className='h-4 w-4 text-[var(--color-brand)]' aria-hidden='true' />
			</div>
			<p className='mt-2 text-3xl font-semibold tracking-tight text-[var(--admin-text-primary)]'>{count}</p>
			<Link
				href={action.target_route}
				className='mt-3 inline-flex items-center gap-1 text-sm font-medium text-[var(--color-brand)] focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45 focus-visible:outline-none'>
				进入练习
				<ArrowUpRight className='h-4 w-4' aria-hidden='true' />
			</Link>
		</Uiv2Card>
	)
}

export function formatWrongRate(wrongRate: number): string {
	return `${Math.round(wrongRate * 100)}%`
}

function WeakTop3Panel({
	items,
	available,
	onRetry
}: {
	items: DashboardWeakKnowledgePoint[]
	available: boolean
	onRetry?: AsyncStateAction
}) {
	return (
		<Uiv2Card>
			<div className='flex items-center justify-between gap-3 border-b border-[var(--admin-border)] pb-3'>
				<h3 className='font-semibold text-[var(--admin-text-primary)]'>薄弱知识点 Top 3</h3>
				<TrendingDown className='h-4 w-4 text-amber-600' aria-hidden='true' />
			</div>
			{!available ? (
				<AsyncStatePanel status='error' title='薄弱知识点暂不可用' error='稍后重试后即可看到薄弱知识点。' onRetry={onRetry} retryLabel='重新尝试' />
			) : items.length === 0 ? (
				<AsyncStatePanel status='empty' title='暂无薄弱知识点' emptyHint='还没有足够的作答记录来判断薄弱点。' />
			) : (
				<ol className='mt-3 divide-y divide-[var(--admin-divider)]'>
					{items.map(item => (
						<li key={item.knowledge_point_id}>
							<Link href={`/manage/knowledge-points/${item.knowledge_point_id}`} className='group flex items-center justify-between gap-4 py-3'>
								<span className='min-w-0'>
									<span className='block truncate text-sm font-medium text-[var(--admin-text-primary)] group-hover:text-[var(--color-brand)]'>{item.name || `知识点 #${item.knowledge_point_id}`}</span>
									<span className='mt-0.5 block text-xs text-[var(--admin-text-tertiary)]'>
										错误率 {formatWrongRate(item.wrong_rate)} · 作答 {item.attempt_count} · 遗忘 {item.lapse_count} · 到期 {item.due_count}
									</span>
								</span>
								<ArrowUpRight className='h-4 w-4 shrink-0 text-[var(--admin-text-tertiary)]' aria-hidden='true' />
							</Link>
						</li>
					))}
				</ol>
			)}
		</Uiv2Card>
	)
}

function RecentlyMasteredPanel({
	items,
	available,
	onRetry
}: {
	items: DashboardRecentlyMasteredItem[]
	available: boolean
	onRetry?: AsyncStateAction
}) {
	return (
		<Uiv2Card>
			<div className='flex items-center justify-between gap-3 border-b border-[var(--admin-border)] pb-3'>
				<h3 className='font-semibold text-[var(--admin-text-primary)]'>最近掌握</h3>
				<Award className='h-4 w-4 text-emerald-600' aria-hidden='true' />
			</div>
			{!available ? (
				<AsyncStatePanel status='error' title='最近掌握暂不可用' error='稍后重试后即可看到最近掌握的内容。' onRetry={onRetry} retryLabel='重新尝试' />
			) : items.length === 0 ? (
				<AsyncStatePanel status='empty' title='暂无最近掌握' emptyHint='还没有进入掌握状态的复习内容。' />
			) : (
				<ul className='mt-3 divide-y divide-[var(--admin-divider)]'>
					{items.map(item => (
						<li key={item.review_item_id}>
							<Link href={`/manage/mistakes/${item.mistake_id}`} className='group flex items-center justify-between gap-4 py-3'>
								<span className='min-w-0'>
									<span className='block truncate text-sm font-medium text-[var(--admin-text-primary)] group-hover:text-[var(--color-brand)]'>{item.question_text}</span>
									<span className='mt-0.5 block text-xs text-[var(--admin-text-tertiary)]'>{formatChineseDateTime(item.mastered_at)}</span>
								</span>
								<ArrowUpRight className='h-4 w-4 shrink-0 text-[var(--admin-text-tertiary)]' aria-hidden='true' />
							</Link>
						</li>
					))}
				</ul>
			)}
		</Uiv2Card>
	)
}

function TodaySection({ summary, onRetry }: DashboardSectionProps) {
	const learningAvailable = summary.sections.learning !== 'unavailable'
	const practiceAvailable = summary.section_actions.practice.available
	const allUnavailable = !learningAvailable && !practiceAvailable
	return (
		<section data-dashboard-section='today' aria-labelledby='today-title' className='space-y-6'>
			<div className='border-b border-[var(--admin-border)] pb-3'>
				<h2 id='today-title' className='font-semibold text-[var(--admin-text-primary)]'>
					今日任务
				</h2>
				<p className='mt-1 text-sm text-[var(--admin-text-secondary)]'>
					{allUnavailable ? '今日摘要暂不可用；不会影响你从题库继续学习。' : '来自 canonical 复习、练习与知识点数据的今日安排。'}
				</p>
			</div>
			<div className='grid gap-5 md:grid-cols-2'>
				<ReviewTodayPanel action={summary.section_actions.review} count={summary.review_today_count} available={learningAvailable} onRetry={onRetry} />
				<PracticeTodayPanel action={summary.section_actions.practice} count={summary.practice_today_count} available={practiceAvailable} onRetry={onRetry} />
			</div>
			<div className='grid gap-5 lg:grid-cols-2'>
				<WeakTop3Panel items={summary.weak_top3} available={learningAvailable} onRetry={onRetry} />
				<RecentlyMasteredPanel items={summary.recently_mastered_4} available={learningAvailable} onRetry={onRetry} />
			</div>
		</section>
	)
}

function StatsSection({ summary }: DashboardSectionProps) {
	const learningAvailable = summary.sections.learning !== 'unavailable'
	return (
		<section data-dashboard-section='stats' aria-labelledby='content-counts-title'>
			<h2 id='content-counts-title' className='border-b border-[var(--admin-border)] pb-3 font-semibold text-[var(--admin-text-primary)]'>
				内容统计
			</h2>
			{learningAvailable ? (
				<div className='grid grid-cols-2 border-b border-[var(--admin-border)] md:grid-cols-4'>
					{countItems.map((item, index) => (
						<Link
							key={item.key}
							href={item.href}
							className={`py-5 ${index % 2 === 0 ? 'border-r' : ''} border-[var(--admin-border)] md:border-r md:px-5 md:first:pl-0 md:last:border-r-0`}>
							<span className='block text-sm text-[var(--admin-text-secondary)]'>{item.label}</span>
							<span className='mt-1 block text-2xl font-semibold tracking-tight text-[var(--admin-text-primary)]'>{summary.counts[item.key]}</span>
						</Link>
					))}
				</div>
			) : (
				<p className='py-4 text-sm text-[var(--admin-text-secondary)]'>内容统计暂不可用</p>
			)}
		</section>
	)
}

function ActivitySection({ summary }: DashboardSectionProps) {
	const activityAvailable = summary.sections.activity !== 'unavailable'
	return (
		<section data-dashboard-section='activity' aria-labelledby='recent-activity-title'>
			<h2 id='recent-activity-title' className='border-b border-[var(--admin-border)] pb-3 font-semibold text-[var(--admin-text-primary)]'>
				最近活动
			</h2>
			{activityAvailable ? (
				<div className='grid gap-8 pt-5 lg:grid-cols-2'>
					<div>
						<h3 className='text-sm font-medium text-[var(--admin-text-secondary)]'>最近题目</h3>
						<div className='mt-2 divide-y divide-[var(--admin-divider)]'>
							{summary.recent_questions.length > 0 ? (
								summary.recent_questions.map(question => (
									<Link key={question.id} href={`/manage/questions/${question.id}`} className='group flex items-center justify-between gap-4 py-3'>
										<span className='min-w-0'>
											<span className='block truncate text-sm font-medium text-[var(--admin-text-primary)] group-hover:text-[var(--color-brand)]'>
												{displayTitle(question.title, question.question_text)}
											</span>
											<span className='mt-0.5 block text-xs text-[var(--admin-text-tertiary)]'>{formatChineseDateTime(question.updated_at)}</span>
										</span>
										<ArrowUpRight className='h-4 w-4 shrink-0 text-[var(--admin-text-tertiary)]' aria-hidden='true' />
									</Link>
								))
							) : (
								<p className='py-4 text-sm text-[var(--admin-text-tertiary)]'>暂无题目</p>
							)}
						</div>
					</div>
					<div>
						<h3 className='text-sm font-medium text-[var(--admin-text-secondary)]'>最近复习</h3>
						<div className='mt-2 divide-y divide-[var(--admin-divider)]'>
							{summary.recent_reviews.length > 0 ? (
								summary.recent_reviews.map(review => (
									<Link key={review.id} href='/manage/review' className='group flex items-center justify-between gap-4 py-3'>
										<span className='min-w-0'>
											<span className='block truncate text-sm font-medium text-[var(--admin-text-primary)] group-hover:text-[var(--color-brand)]'>{review.question_text}</span>
											<span className='mt-0.5 block text-xs text-[var(--admin-text-tertiary)]'>
												评分 {review.rating} · {formatChineseDateTime(review.reviewed_at)}
											</span>
										</span>
										<ArrowUpRight className='h-4 w-4 shrink-0 text-[var(--admin-text-tertiary)]' aria-hidden='true' />
									</Link>
								))
							) : (
								<p className='py-4 text-sm text-[var(--admin-text-tertiary)]'>暂无复习记录</p>
							)}
						</div>
					</div>
				</div>
			) : (
				<p className='pt-4 text-sm text-[var(--admin-text-secondary)]'>最近活动暂不可用</p>
			)}
		</section>
	)
}

function StorageSection({ summary }: DashboardSectionProps) {
	const storageHealthy = summary.sections.storage !== 'unknown' && summary.system.storage === 'ok'
	return (
		<section data-dashboard-section='storage' aria-labelledby='system-status-title'>
			<h2 id='system-status-title' className='border-b border-[var(--admin-border)] pb-3 font-semibold text-[var(--admin-text-primary)]'>
				系统状态
			</h2>
			<div className='flex flex-wrap items-center gap-x-6 gap-y-3 pt-4 text-sm'>
				<span className='inline-flex items-center gap-2 text-emerald-700'>
					<CheckCircle2 className='h-4 w-4' aria-hidden='true' />
					<Uiv2Badge text='服务正常' tone='neutral' />
				</span>
				<span className={`inline-flex items-center gap-2 ${summary.system.database === 'ok' ? 'text-emerald-700' : 'text-amber-700'}`}>
					{summary.system.database === 'ok' ? <CheckCircle2 className='h-4 w-4' aria-hidden='true' /> : <CircleHelp className='h-4 w-4' aria-hidden='true' />}
					<Uiv2Badge text={summary.system.database === 'ok' ? '数据库正常' : '数据库状态未知'} tone='neutral' />
				</span>
				<span className={`inline-flex items-center gap-2 ${storageHealthy ? 'text-emerald-700' : 'text-amber-700'}`}>
					{storageHealthy ? <CheckCircle2 className='h-4 w-4' aria-hidden='true' /> : <CircleHelp className='h-4 w-4' aria-hidden='true' />}
					<Uiv2Badge
						text={summary.sections.storage === 'empty' ? '暂无附件' : storageHealthy ? '附件存储正常' : '附件存储状态未知'}
						tone='neutral'
					/>
				</span>
			</div>
		</section>
	)
}

function renderDashboardSection(section: HomeSection, summary: DashboardSummary, onRetry?: () => void) {
	if (section === 'today') return <TodaySection key={section} summary={summary} onRetry={onRetry} />
	if (section === 'activity') return <ActivitySection key={section} summary={summary} />
	if (section === 'stats') return <StatsSection key={section} summary={summary} />
	return <StorageSection key={section} summary={summary} />
}

export function DashboardOverview({ summary, profile, profileError, profileLoading = false, profileUnavailable = false, onProfileRetry, onSummaryRetry }: DashboardOverviewProps) {
	const preferences = normalizeHomePreferences(profile?.home_preferences)
	const visibleSections = preferences.section_order.filter(section => !preferences.hidden_sections.includes(section))
	const learningAvailable = summary.sections.learning !== 'unavailable'
	const practiceAvailable = summary.section_actions.practice.available

	return (
		<div
			className='space-y-10 rounded-[16px] border p-4 sm:p-6'
			data-surface='admin'
			style={{ background: 'var(--admin-bg)', borderColor: 'var(--admin-border)', color: 'var(--admin-text-primary)' }}>
			{profileLoading ? (
				<AsyncStatePanel status='loading' loadingLabel='正在加载个人资料' skeletonRows={2} />
			) : profileError || profileUnavailable ? (
				<AsyncStatePanel status='error' title={profileUnavailable && !profileError ? '个人资料暂不可用' : '个人资料加载失败'} error={profileError ?? '学习摘要仍可使用；稍后可重试加载私有欢迎区域。'} onRetry={onProfileRetry} retryLabel='重新加载个人资料' />
			) : profile ? (
				profile.home_preferences.show_welcome ? (
					<section aria-labelledby='private-welcome-title' className='rounded-2xl border border-[var(--color-brand)]/15 bg-[var(--color-brand)]/5 px-5 py-4'>
						<p className='text-xs font-medium tracking-[0.12em] text-[var(--color-brand)] uppercase'>个人学习</p>
						<h2 id='private-welcome-title' className='mt-2 text-xl font-semibold text-[var(--admin-text-primary)]'>
							{getWelcomeGreeting(profile)}
						</h2>
						<p className='mt-1 text-sm text-[var(--admin-text-secondary)]'>{profile.welcome_message || profile.signature || '按自己的节奏继续积累。'}</p>
						<p className='mt-2 text-xs text-[var(--admin-text-tertiary)]'>当前时间：{formatProfileTime(profile)}</p>
					</section>
				) : null
			) : null}
			<div>
				<p className='text-xs font-medium tracking-[0.16em] text-[var(--brand,#3db8a8)] uppercase'>学习空间</p>
				<Uiv2PageHeader title='学习管理首页' subtitle={`数据更新于 ${formatChineseDateTime(summary.generated_at)}`} />
			</div>
			<QuickActionsSection />
			<TodayFirstActionBanner action={summary.today_first_action} unavailable={!learningAvailable && !practiceAvailable} onRetry={onSummaryRetry} />
			<div className='space-y-10'>{visibleSections.map(section => renderDashboardSection(section, summary, onSummaryRetry))}</div>
		</div>
	)
}
