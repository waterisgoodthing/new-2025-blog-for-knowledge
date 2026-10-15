import type { AnalyticsModel, TrendPoint } from '../../../contracts/ui-v2/analytics'
import type { MasteryScore } from '../../../contracts/ui-v2/mastery'
import type { UiPageModel } from '../../../contracts/ui-v2/ui-state'
import { Uiv2Badge } from '../../../components/ui-v2/Badge'
import { Uiv2Card } from '../../../components/ui-v2/Card'
import { Uiv2SourceBadge } from '../../../components/ui-v2/DomainBadges'
import { Uiv2PageStateView } from '../../../components/ui-v2/PageStateView'
import { Uiv2Progress } from '../../../components/ui-v2/Progress'
import { Uiv2SectionHeader } from '../../../components/ui-v2/SectionHeader'

/** Mastery display (U9): value or honest empty copy. No algorithm, no gauge fakery. */
export function Uiv2MasteryIndicator({ mastery }: { mastery: MasteryScore }) {
	if (mastery.value === null) {
		return <p>暂无足够数据，数据积累中</p>
	}
	return (
		<div>
			<p>
				掌握度 <strong>{mastery.value}</strong>
			</p>
			<Uiv2Progress value={mastery.value} />
		</div>
	)
}

/** Text-first trend list (U9). A chart can replace this when real data exists. */
export function Uiv2LearningTrend({ points }: { points: TrendPoint[] }) {
	if (points.length === 0) {
		return <p>暂无足够数据，数据积累中</p>
	}
	return (
		<ul className="flex flex-col gap-1">
			{points.map(point => (
				<li key={point.label}>
					{point.label}：{point.value === null ? '缺数据' : point.value}
				</li>
			))}
		</ul>
	)
}

export interface Uiv2AnalyticsSectionProps {
	model: UiPageModel<AnalyticsModel>
	onRetry?: () => void
}

/** Analytics section (U9): only data-backed presentation, honest empty states. */
export function Uiv2AnalyticsSection({ model, onRetry }: Uiv2AnalyticsSectionProps) {
	return (
		<section aria-label="学习分析">
			<Uiv2SectionHeader title="分析" description="掌握度、薄弱点与学习趋势：有数据才展示" />
			<div className="pt-2">
				<Uiv2SourceBadge source={model.source} />
			</div>
			<Uiv2PageStateView
				model={model}
				loadingLabel="正在加载学习分析"
				emptyHint="还没有可分析的数据，先积累一些学习记录吧。"
				onRetry={onRetry}
			>
				{data => (
					<div className="grid gap-4 md:grid-cols-2">
						<Uiv2Card title="掌握度">
							<Uiv2MasteryIndicator mastery={data.mastery} />
						</Uiv2Card>
						<Uiv2Card title="复习完成情况">
							{data.reviewCompletion.completed === null || data.reviewCompletion.total === null ? (
								<p>暂无足够数据，数据积累中</p>
							) : (
								<p>
									已完成 <strong>{data.reviewCompletion.completed}</strong> / 共{' '}
									<strong>{data.reviewCompletion.total}</strong>
								</p>
							)}
						</Uiv2Card>
						<Uiv2Card title="学习趋势">
							<Uiv2LearningTrend points={data.learningTrend} />
						</Uiv2Card>
						<Uiv2Card title="错题趋势">
							{data.mistakeTrend.length === 0 ? (
								<p>暂无足够数据，数据积累中</p>
							) : (
								<ul className="flex flex-col gap-1">
									{data.mistakeTrend.map(point => (
										<li key={point.label}>
											{point.label}：新增 {point.newMistakes ?? '缺数据'} · 解决{' '}
											{point.resolvedMistakes ?? '缺数据'}
										</li>
									))}
								</ul>
							)}
						</Uiv2Card>
						<Uiv2Card title="薄弱点分布">
							{data.weaknessDistribution.length === 0 ? (
								<p>暂无足够数据，数据积累中</p>
							) : (
								<ul className="flex flex-col gap-2">
									{data.weaknessDistribution.map(item => (
										<li key={item.name} className="flex items-center gap-2">
											<Uiv2Badge text={item.name} tone="mistake" />
											<span className="text-[var(--uiv2-text-secondary)]">
												{item.count === null ? '数据积累中' : `${item.count} 道`}
												{item.share !== null ? ` · 占比 ${Math.round(item.share * 100)}%` : ''}
											</span>
										</li>
									))}
								</ul>
							)}
						</Uiv2Card>
					</div>
				)}
			</Uiv2PageStateView>
		</section>
	)
}
