import type { StudyTask } from '../../../contracts/ui-v2/study-task'
import type { UiPageModel } from '../../../contracts/ui-v2/ui-state'
import { Uiv2Badge } from '../../../components/ui-v2/Badge'
import { Uiv2Card } from '../../../components/ui-v2/Card'
import { Uiv2SourceBadge } from '../../../components/ui-v2/DomainBadges'
import { Uiv2PageStateView } from '../../../components/ui-v2/PageStateView'
import { Uiv2SectionHeader } from '../../../components/ui-v2/SectionHeader'

const KIND_LABEL: Record<StudyTask['kind'], string> = {
	review: '复习',
	mistake_retry: '错题重做',
	new_practice: '新练习',
	note_review: '笔记回顾',
}

const STATUS_LABEL: Record<StudyTask['status'], string> = {
	pending: '待开始',
	in_progress: '进行中',
	completed: '已完成',
	overdue: '已逾期',
}

export function Uiv2StudyTaskCard({ task }: { task: StudyTask }) {
	return (
		<Uiv2Card title={task.title}>
			<div className="flex flex-wrap items-center gap-2">
				<Uiv2Badge text={KIND_LABEL[task.kind]} tone="neutral" />
				<Uiv2Badge
					text={STATUS_LABEL[task.status]}
					tone={task.status === 'overdue' ? 'mistake' : 'neutral'}
				/>
				<span className="text-[var(--uiv2-text-secondary)]">
					{task.subject}
					{task.dueAt ? ` · 截止 ${task.dueAt}` : ''}
				</span>
			</div>
			{task.provenanceNote ? (
				<p role="note" className="text-[var(--uiv2-text-secondary)]">
					{task.provenanceNote}
				</p>
			) : null}
			<a
				href={task.href}
				className="inline-flex min-h-[40px] items-center focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]"
			>
				进入学习任务
			</a>
		</Uiv2Card>
	)
}

export interface Uiv2TodaySectionProps {
	model: UiPageModel<StudyTask[]>
	onRetry?: () => void
}

/** “今天学什么”入口（U3）。来源诚实标注；统一任务流缺失时显示 BLOCKED 提示。 */
export function Uiv2TodaySection({ model, onRetry }: Uiv2TodaySectionProps) {
	return (
		<section aria-label="今日任务">
			<Uiv2SectionHeader title="今天学什么" description="今天的学习入口：复习到期内容，补上薄弱点" />
			<div className="pt-2">
				<Uiv2SourceBadge source={model.source} />
			</div>
			<Uiv2PageStateView
				model={model}
				loadingLabel="正在加载今日任务"
				emptyHint="今天没有安排。先去题库或复习页看看？"
				onRetry={onRetry}
			>
				{tasks => (
					<ul className="grid gap-4 md:grid-cols-2">
						{tasks.map(task => (
							<li key={task.id}>
								<Uiv2StudyTaskCard task={task} />
							</li>
						))}
					</ul>
				)}
			</Uiv2PageStateView>
		</section>
	)
}
