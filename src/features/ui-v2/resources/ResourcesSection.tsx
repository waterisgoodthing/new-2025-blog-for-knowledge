import type { ResourceItem } from '../../../contracts/ui-v2/resource'
import type { UiPageModel } from '../../../contracts/ui-v2/ui-state'
import { Uiv2Badge } from '../../../components/ui-v2/Badge'
import { Uiv2Card } from '../../../components/ui-v2/Card'
import { Uiv2SourceBadge } from '../../../components/ui-v2/DomainBadges'
import { Uiv2PageStateView } from '../../../components/ui-v2/PageStateView'
import { Uiv2SectionHeader } from '../../../components/ui-v2/SectionHeader'

export function Uiv2ResourceCard({ resource }: { resource: ResourceItem }) {
	return (
		<Uiv2Card title={resource.name}>
			<div className="flex flex-wrap items-center gap-2">
				<Uiv2Badge text={resource.mimeType} tone="neutral" />
				<span className="text-[var(--uiv2-text-secondary)]">
					{resource.sizeLabel ?? '大小未知'} · 上传于 {resource.uploadedAt}
				</span>
			</div>
		</Uiv2Card>
	)
}

export interface Uiv2ResourcesSectionProps {
	model: UiPageModel<ResourceItem[]>
	onRetry?: () => void
}

/** Resources section (U10): attachments display. No new backend domain. */
export function Uiv2ResourcesSection({ model, onRetry }: Uiv2ResourcesSectionProps) {
	return (
		<section aria-label="学习资料">
			<Uiv2SectionHeader title="资料" description="学习附件：图片、手写推导与参考文件" />
			<div className="pt-2">
				<Uiv2SourceBadge source={model.source} />
			</div>
			<Uiv2PageStateView
				model={model}
				loadingLabel="正在加载资料"
				emptyHint="还没有上传任何资料。"
				onRetry={onRetry}
			>
				{resources => (
					<ul className="grid gap-4 md:grid-cols-2">
						{resources.map(resource => (
							<li key={resource.id}>
								<Uiv2ResourceCard resource={resource} />
							</li>
						))}
					</ul>
				)}
			</Uiv2PageStateView>
		</section>
	)
}
