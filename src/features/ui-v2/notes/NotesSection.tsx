import type { NoteArtifact } from '../../../contracts/ui-v2/note-artifact'
import type { UiPageModel } from '../../../contracts/ui-v2/ui-state'
import { Uiv2Badge } from '../../../components/ui-v2/Badge'
import { Uiv2Card } from '../../../components/ui-v2/Card'
import { Uiv2SourceBadge } from '../../../components/ui-v2/DomainBadges'
import { Uiv2SubjectBadge } from '../../../components/ui-v2/DomainBadges'
import { Uiv2PageStateView } from '../../../components/ui-v2/PageStateView'
import { Uiv2SectionHeader } from '../../../components/ui-v2/SectionHeader'

export function Uiv2NoteArtifactCard({ note }: { note: NoteArtifact }) {
	return (
		<Uiv2Card title={note.title}>
			{note.summary ? (
				<p className="text-[var(--uiv2-text-secondary)]">{note.summary}</p>
			) : (
				<p role="note" className="text-[var(--uiv2-text-secondary)]">
					暂无摘要
				</p>
			)}
			<div className="flex flex-wrap items-center gap-2">
				<Uiv2SubjectBadge label={note.subjectLabel} />
				{note.knowledgePoints.map(point => (
					<Uiv2Badge key={point} text={point} tone="neutral" />
				))}
				{note.tags.map(tag => (
					<Uiv2Badge key={tag} text={`#${tag}`} tone="neutral" />
				))}
			</div>
			<a
				href={note.editorHref}
				className="inline-flex min-h-[40px] items-center focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--uiv2-brand)]"
			>
				在编辑器中打开
			</a>
		</Uiv2Card>
	)
}

export interface Uiv2NotesSectionProps {
	model: UiPageModel<NoteArtifact[]>
	onRetry?: () => void
}

/** Notes as Learning Knowledge Artifacts (U8). Editor linked, not rebuilt. */
export function Uiv2NotesSection({ model, onRetry }: Uiv2NotesSectionProps) {
	return (
		<section aria-label="学习笔记">
			<Uiv2SectionHeader title="笔记" description="学习知识沉淀：关联科目与知识点，需要时回到编辑器" />
			<div className="pt-2">
				<Uiv2SourceBadge source={model.source} />
			</div>
			<Uiv2PageStateView
				model={model}
				loadingLabel="正在加载笔记"
				emptyHint="还没有笔记，学完一个知识点后记一笔吧。"
				onRetry={onRetry}
			>
				{notes => (
					<ul className="grid gap-4 md:grid-cols-2">
						{notes.map(note => (
							<li key={note.id}>
								<Uiv2NoteArtifactCard note={note} />
							</li>
						))}
					</ul>
				)}
			</Uiv2PageStateView>
		</section>
	)
}
