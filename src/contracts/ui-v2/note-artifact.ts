// UI-facing contract: note as a Learning Knowledge Artifact (U8).
// Notes keep their value but no longer define the product IA: list / detail /
// editor-entry / knowledge-relation / subject-relation display fields only.
// The editor itself is owned elsewhere (dirty files, READ-ONLY) — this track
// only links to the existing editor entry, never reimplements it.

import type { MasterySource } from './mastery'

export interface NoteArtifact {
	id: string
	slug: string
	title: string
	summary: string | null
	subjectLabel: string | null
	knowledgePoints: string[]
	tags: string[]
	updatedAt: string
	/** Link to the existing editor entry (owned elsewhere, not reimplemented). */
	editorHref: string
	source: MasterySource
}
