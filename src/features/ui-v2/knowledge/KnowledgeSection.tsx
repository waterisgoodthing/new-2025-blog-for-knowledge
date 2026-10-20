import type { KnowledgeNode, LearningState } from '../../../contracts/ui-v2/knowledge'
import type { UiPageModel } from '../../../contracts/ui-v2/ui-state'
import { Uiv2Badge } from '../../../components/ui-v2/Badge'
import { Uiv2Card } from '../../../components/ui-v2/Card'
import { Uiv2SourceBadge } from '../../../components/ui-v2/DomainBadges'
import { Uiv2PageStateView } from '../../../components/ui-v2/PageStateView'
import { Uiv2SectionHeader } from '../../../components/ui-v2/SectionHeader'

const STATE_LABEL: Record<LearningState, string> = {
	not_started: '未开始',
	learning: '学习中',
	reviewing: '复习中',
	unknown: '数据积累中',
}

function countText(value: number | null, unit: string): string {
	return value === null ? '数据积累中' : `${value} ${unit}`
}

export function Uiv2KnowledgeCard({ node, depth = 0 }: { node: KnowledgeNode; depth?: number }) {
	return (
		<Uiv2Card title={node.name}>
			<div className="flex flex-wrap items-center gap-2">
				<Uiv2Badge
					text={node.kind === 'subject' ? '科目' : '知识点'}
					tone={node.kind === 'subject' ? 'note' : 'neutral'}
				/>
				<Uiv2Badge text={STATE_LABEL[node.learningState]} tone="neutral" />
			</div>
			{node.description ? (
				<p className="text-[var(--uiv2-text-secondary)]">{node.description}</p>
			) : null}
			<ul className="flex flex-wrap gap-x-4 gap-y-1 text-[var(--uiv2-text-secondary)]">
				<li>题目：{countText(node.relatedQuestions, '道')}</li>
				<li>错题：{countText(node.relatedMistakes, '道')}</li>
				<li>笔记：{countText(node.relatedNotes, '篇')}</li>
			</ul>
			{node.children.length > 0 ? (
				<ul className="flex flex-col gap-3">
					{node.children.map(child => (
						<li key={child.id}>
							<Uiv2KnowledgeCard node={child} depth={depth + 1} />
						</li>
					))}
				</ul>
			) : null}
		</Uiv2Card>
	)
}

export interface Uiv2KnowledgeSectionProps {
	model: UiPageModel<KnowledgeNode[]>
	onRetry?: () => void
}

/** Knowledge section (U7): subjects + points + learning state + relations. */
export function Uiv2KnowledgeSection({ model, onRetry }: Uiv2KnowledgeSectionProps) {
	return (
		<section aria-label="知识体系">
			<Uiv2SectionHeader title="知识" description="科目与知识点：学习状态与关联内容一目了然" />
			<div className="pt-2">
				<Uiv2SourceBadge source={model.source} />
			</div>
			<Uiv2PageStateView
				model={model}
				loadingLabel="正在加载知识体系"
				emptyHint="还没有科目，先去创建一个吧。"
				onRetry={onRetry}
			>
				{nodes => (
					<ul className="grid gap-4 md:grid-cols-2">
						{nodes.map(node => (
							<li key={node.id}>
								<Uiv2KnowledgeCard node={node} />
							</li>
						))}
					</ul>
				)}
			</Uiv2PageStateView>
		</section>
	)
}
