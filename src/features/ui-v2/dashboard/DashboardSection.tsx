import type { DashboardModel, DashboardNextAction } from '../../../contracts/ui-v2/dashboard'
import type { UiPageModel } from '../../../contracts/ui-v2/ui-state'
import { Uiv2Badge } from '../../../components/ui-v2/Badge'
import { Uiv2Card } from '../../../components/ui-v2/Card'
import { Uiv2SourceBadge } from '../../../components/ui-v2/DomainBadges'
import { Uiv2PageStateView } from '../../../components/ui-v2/PageStateView'
import { Uiv2SectionHeader } from '../../../components/ui-v2/SectionHeader'

function countText(value: number | null): string {
	return value === null ? '暂无足够数据' : String(value)
}

export function Uiv2NextActionCard({ action }: { action: DashboardNextAction }) {
	return (
		<Uiv2Card title="下一步">
			<p>{action.title}</p>
			<p className="text-[var(--uiv2-text-secondary)]">{action.reason}</p>
			<a
				href={action.href}
				className="inline-flex min-h-[40px] items-center focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]"
			>
				前往处理
			</a>
		</Uiv2Card>
	)
}

export interface Uiv2DashboardSectionProps {
	model: UiPageModel<DashboardModel>
	onRetry?: () => void
}

/**
 * Dashboard learning-first section (U2): Today / Review / Weakness /
 * Recent / Trend / Next Action. Honest empty states; no CMS counters.
 */
export function Uiv2DashboardSection({ model, onRetry }: Uiv2DashboardSectionProps) {
	return (
		<section aria-label="学习仪表盘">
			<Uiv2SectionHeader title="今日学习" description="从薄弱点出发，决定今天学什么" />
			<div className="pt-2">
				<Uiv2SourceBadge source={model.source} />
			</div>
			<Uiv2PageStateView model={model} loadingLabel="正在加载仪表盘" emptyHint="还没有学习数据，先去题库做几道题吧" onRetry={onRetry}>
				{data => (
					<div className="grid gap-4 md:grid-cols-2">
						<Uiv2Card title="今日任务">
							<p>
								到期 <strong>{countText(data.today.dueCount)}</strong>
								{data.today.overdueCount !== null && data.today.overdueCount > 0 ? (
									<>
										{' '}（逾期 <strong>{data.today.overdueCount}</strong>）
									</>
								) : null}
							</p>
							{data.today.dueCount === null ? <p>数据积累中</p> : null}
						</Uiv2Card>
						<Uiv2Card title="复习">
							<p>
								待复习 <strong>{countText(data.review.pendingCount)}</strong>
								{' '}· 今日到期 <strong>{countText(data.review.dueTodayCount)}</strong>
							</p>
						</Uiv2Card>
						<Uiv2Card title="薄弱点">
							{data.weaknesses.length === 0 ? (
								<p>暂无足够数据，数据积累中</p>
							) : (
								<ul className="flex flex-col gap-2">
									{data.weaknesses.map(w => (
										<li key={w.name} className="flex items-center gap-2">
											<Uiv2Badge text={w.name} tone="mistake" />
											<span className="text-[var(--uiv2-text-secondary)]">
												{w.count === null ? '数据积累中' : `${w.count} 道错题`}
												{w.subjects.length > 0 ? ` · ${w.subjects.join('、')}` : ''}
											</span>
										</li>
									))}
								</ul>
							)}
						</Uiv2Card>
						<Uiv2Card title="最近学习">
							{data.recent.length === 0 ? (
								<p>还没有学习记录</p>
							) : (
								<ul className="flex flex-col gap-2">
									{data.recent.map(r => (
										<li key={r.id} className="flex items-center gap-2">
											<Uiv2Badge
												text={r.kind === 'question' ? '题目' : r.kind === 'mistake' ? '错题' : '复习'}
												tone={r.kind === 'mistake' ? 'mistake' : r.kind === 'question' ? 'note' : 'neutral'}
											/>
											<span>{r.title}</span>
										</li>
									))}
								</ul>
							)}
						</Uiv2Card>
						<Uiv2Card title="学习趋势">
							{data.trend.length === 0 ? (
								<p>暂无足够数据，数据积累中</p>
							) : (
								<ul className="flex flex-col gap-1">
									{data.trend.map(t => (
										<li key={t.label}>
											{t.label}：{t.value === null ? '缺数据' : t.value}
										</li>
									))}
								</ul>
							)}
						</Uiv2Card>
						{data.nextAction ? <Uiv2NextActionCard action={data.nextAction} /> : null}
					</div>
				)}
			</Uiv2PageStateView>
		</section>
	)
}
