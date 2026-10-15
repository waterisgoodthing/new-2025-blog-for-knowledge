import { useState } from 'react'

import type { LearningSettings } from '../../../contracts/ui-v2/settings'
import type { UiPageModel } from '../../../contracts/ui-v2/ui-state'
import { Uiv2Card } from '../../../components/ui-v2/Card'
import { Uiv2SourceBadge } from '../../../components/ui-v2/DomainBadges'
import { Uiv2PageStateView } from '../../../components/ui-v2/PageStateView'
import { Uiv2SectionHeader } from '../../../components/ui-v2/SectionHeader'

export interface Uiv2SettingsSectionProps {
	model: UiPageModel<LearningSettings>
	onRetry?: () => void
}

/**
 * Learning settings section (U11): display preferences local to the view.
 * No auth, no account mutation, no persistence claims — the note says so.
 */
export function Uiv2SettingsSection({ model, onRetry }: Uiv2SettingsSectionProps) {
	// View-local draft: starts from the loaded settings on first edit, so the
	// loaded values are never clobbered by defaults.
	const [draft, setDraft] = useState<LearningSettings | null>(null)

	return (
		<section aria-label="学习设置">
			<Uiv2SectionHeader title="设置" description="与学习直接相关的显示偏好" />
			<div className="pt-2">
				<Uiv2SourceBadge source={model.source} />
			</div>
			<Uiv2PageStateView
				model={model}
				loadingLabel="正在加载学习设置"
				emptyHint="还没有可用的学习设置。"
				onRetry={onRetry}
			>
				{settings => {
					const current = draft ?? settings
					const update = (patch: Partial<LearningSettings>) =>
						setDraft({ ...current, ...patch })
					return (
						<div className="grid gap-4 md:grid-cols-2">
							<Uiv2Card title="每日复习目标">
								<label className="flex min-h-[40px] items-center gap-2">
									目标数量
									<input
										type="number"
										min={0}
										max={200}
										value={current.dailyReviewGoal ?? ''}
										placeholder="未设置"
										aria-label="每日复习目标数量"
										onChange={event => {
											const parsed =
												event.target.value === '' ? null : Number(event.target.value)
											update({
												dailyReviewGoal:
													typeof parsed === 'number' && Number.isFinite(parsed) ? parsed : null,
											})
										}}
										className="min-h-[40px] w-28 rounded-[var(--uiv2-radius-sm)] border border-[var(--uiv2-border)] bg-white px-3 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]"
									/>
								</label>
							</Uiv2Card>
							<Uiv2Card title="显示">
								<label className="flex min-h-[40px] items-center gap-2">
									<input
										type="checkbox"
										checked={current.showMasteryDetails}
										onChange={event => update({ showMasteryDetails: event.target.checked })}
									/>
									显示掌握度详情
								</label>
								<fieldset>
									<legend>内容密度</legend>
									<label className="flex min-h-[40px] items-center gap-2">
										<input
											type="radio"
											name="uiv2-density"
											value="comfortable"
											checked={current.density === 'comfortable'}
											onChange={() => update({ density: 'comfortable' })}
										/>
										舒适
									</label>
									<label className="flex min-h-[40px] items-center gap-2">
										<input
											type="radio"
											name="uiv2-density"
											value="compact"
											checked={current.density === 'compact'}
											onChange={() => update({ density: 'compact' })}
										/>
										紧凑
									</label>
								</fieldset>
							</Uiv2Card>
							<p role="note" className="text-[var(--uiv2-text-secondary)] md:col-span-2">
								偏好仅保存在当前视图，不修改账号与登录设置。
							</p>
						</div>
					)
				}}
			</Uiv2PageStateView>
		</section>
	)
}
