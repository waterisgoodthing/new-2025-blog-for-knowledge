// UI-facing contract: resource item (U10).
// Display mapping of the existing attachments model (src/lib/api/attachments.ts,
// read-only). No new backend domain is invented: there is no canonical
// "resource" domain beyond attachments (GAP-007).

import type { MasterySource } from './mastery'

export interface ResourceItem {
	id: string
	name: string
	mimeType: string
	/** Human-readable size (e.g. "12 KB"); null when unknown. */
	sizeLabel: string | null
	uploadedAt: string
	source: MasterySource
}

export function formatBytes(sizeBytes: number | null | undefined): string | null {
	if (typeof sizeBytes !== 'number' || !Number.isFinite(sizeBytes) || sizeBytes < 0) {
		return null
	}
	if (sizeBytes < 1024) return `${sizeBytes} B`
	if (sizeBytes < 1024 * 1024) return `${Math.round(sizeBytes / 1024)} KB`
	return `${Math.round((sizeBytes / (1024 * 1024)) * 10) / 10} MB`
}
