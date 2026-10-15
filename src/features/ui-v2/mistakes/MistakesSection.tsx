import type { MistakeCardModel, MistakeFilterModel } from '../../../contracts/ui-v2/mistake'
import type { UiPageModel } from '../../../contracts/ui-v2/ui-state'
import { Uiv2Badge } from '../../../components/ui-v2/Badge'
import { Uiv2Card } from '../../../components/ui-v2/Card'
import { Uiv2DifficultyBadge, Uiv2SourceBadge, Uiv2SubjectBadge } from '../../../components/ui-v2/DomainBadges'
import { Uiv2PageStateView } from '../../../components/ui-v2/PageStateView'
import { Uiv2SectionHeader } from '../../../components/ui-v2/SectionHeader'

const REASON_LABEL: Record<MistakeCardModel['reasonCategory'], string> = {
	concept: '概念理解',
	calculation: '计算失误',
	reading: '审题偏差',
	careless: '粗心',
	unknown: '待归类',
}

export function Uiv2MistakeCard({ mistake }: { mistake: MistakeCardModel }) {
	return (
		<Uiv2Card title={mistake.title}>
			<p className="text-[var(--uiv2-text-secondary)]">{mistake.questionText}</p>
			<div className="flex flex-wrap items-center gap-2">
				<Uiv2Badge text={REASON_LABEL[mistake.reasonCategory]} tone="mistake" />
				<Uiv2DifficultyBadge difficulty={mistake.difficulty} />
				<Uiv2SubjectBadge label={mistake.subjectLabel} />
				<Uiv2Badge
					text={mistake.status === 'active' ? '跟进中' : '已归档'}
					tone="neutral"
				/>
				{mistake.knowledgePointIds.length > 0 ? (
					<span className="text-[var(--uiv2-text-secondary)]">
						关联 {mistake.knowledgePointIds.length} 个知识点
					</span>
				) : (
					<span className="text-[var(--uiv2-text-secondary)]">未关联知识点</span>
				)}
			</div>
			{mistake.reviewItemId ? (
				<a
					href="/manage/review"
					className="inline-flex min-h-[40px] items-center focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]"
				>
					进入复习
				</a>
			) : (
				<p role="note" className="text-[var(--uiv2-text-secondary)]">
					暂无复习安排
				</p>
			)}
		</Uiv2Card>
	)
}

const REASON_OPTIONS: Array<{ value: MistakeFilterModel['reason']; label: string }> = [
	{ value: 'all', label: '全部原因' },
	{ value: 'concept', label: '概念理解' },
	{ value: 'calculation', label: '计算失误' },
	{ value: 'reading', label: '审题偏差' },
	{ value: 'careless', label: '粗心' },
	{ value: 'unknown', label: '待归类' },
]

export interface Uiv2MistakeFilterProps {
	filter: MistakeFilterModel
	onChange: (next: MistakeFilterModel) => void
}

/** Mistake list filter (U4): status / reason / text query. Labelled controls. */
export function Uiv2MistakeFilter({ filter, onChange }: Uiv2MistakeFilterProps) {
	return (
		<form
			aria-label="错题筛选"
			className="flex flex-wrap gap-3"
			onSubmit={event => event.preventDefault()}
		>
			<label className="flex min-h-[40px] items-center gap-2 text-[var(--uiv2-text-sm)]">
				状态
				<select
					value={filter.status}
					onChange={event =>
						onChange({ ...filter, status: event.target.value as MistakeFilterModel['status'] })
					}
					className="min-h-[40px] rounded-[var(--uiv2-radius-sm)] border border-[var(--uiv2-border)] bg-white px-2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]"
				>
					<option value="all">全部状态</option>
					<option value="active">跟进中</option>
					<option value="archived">已归档</option>
				</select>
			</label>
			<label className="flex min-h-[40px] items-center gap-2 text-[var(--uiv2-text-sm)]">
				原因
				<select
					value={filter.reason}
					onChange={event =>
						onChange({ ...filter, reason: event.target.value as MistakeFilterModel['reason'] })
					}
					className="min-h-[40px] rounded-[var(--uiv2-radius-sm)] border border-[var(--uiv2-border)] bg-white px-2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]"
				>
					{REASON_OPTIONS.map(option => (
						<option key={option.value} value={option.value}>
							{option.label}
						</option>
					))}
				</select>
			</label>
			<label className="flex min-h-[40px] items-center gap-2 text-[var(--uiv2-text-sm)]">
				搜索
				<input
					type="search"
					value={filter.query}
					placeholder="按标题或题干搜索"
					aria-label="按标题或题干搜索错题"
					onChange={event => onChange({ ...filter, query: event.target.value })}
					className="min-h-[40px] rounded-[var(--uiv2-radius-sm)] border border-[var(--uiv2-border)] bg-white px-3 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]"
				/>
			</label>
		</form>
	)
}

/** Pure client-side filtering shared by the section and tests. */
export function applyMistakeFilter(
	mistakes: MistakeCardModel[],
	filter: MistakeFilterModel,
): MistakeCardModel[] {
	const query = filter.query.trim().toLowerCase()
	return mistakes.filter(mistake => {
		if (filter.status !== 'all' && mistake.status !== filter.status) return false
		if (filter.reason !== 'all' && mistake.reasonCategory !== filter.reason) return false
		if (
			filter.knowledgePointId !== null &&
			!mistake.knowledgePointIds.includes(filter.knowledgePointId)
		)
			return false
		if (
			query &&
			!`${mistake.title} ${mistake.questionText}`.toLowerCase().includes(query)
		)
			return false
		return true
	})
}

export interface Uiv2MistakesSectionProps {
	model: UiPageModel<MistakeCardModel[]>
	filter: MistakeFilterModel
	onFilterChange: (next: MistakeFilterModel) => void
	onRetry?: () => void
}

/** Canonical mistake UX section (U4): filter + list + review entry + states. */
export function Uiv2MistakesSection({
	model,
	filter,
	onFilterChange,
	onRetry,
}: Uiv2MistakesSectionProps) {
	return (
		<section aria-label="错题">
			<Uiv2SectionHeader title="错题" description="已确认的错题：复盘原因，安排复习" />
			<div className="pt-2">
				<Uiv2SourceBadge source={model.source} />
			</div>
			<Uiv2MistakeFilter filter={filter} onChange={onFilterChange} />
			<Uiv2PageStateView
				model={model}
				loadingLabel="正在加载错题"
				emptyHint="还没有错题。做错的题目确认后会出现在这里。"
				onRetry={onRetry}
			>
				{mistakes => {
					const visible = applyMistakeFilter(mistakes, filter)
					if (visible.length === 0) {
						return <p>没有符合筛选条件的错题，换个条件试试。</p>
					}
					return (
						<ul className="grid gap-4 md:grid-cols-2">
							{visible.map(mistake => (
								<li key={mistake.id}>
									<Uiv2MistakeCard mistake={mistake} />
								</li>
							))}
						</ul>
					)
				}}
			</Uiv2PageStateView>
		</section>
	)
}
