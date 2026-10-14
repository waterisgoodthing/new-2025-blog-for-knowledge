// UI-facing contract: learning settings display (U11).
// Learning-related display preferences only. Auth, session, admin profile,
// and any backend mutation are OUT of scope. Values here are view-local until
// a settings contract is approved; the UI labels that honestly.

import type { MasterySource } from './mastery'

export type LearningDensity = 'comfortable' | 'compact'

export interface LearningSettings {
	dailyReviewGoal: number | null
	density: LearningDensity
	showMasteryDetails: boolean
	source: MasterySource
}

export const DEFAULT_LEARNING_SETTINGS: LearningSettings = {
	dailyReviewGoal: null,
	density: 'comfortable',
	showMasteryDetails: true,
	source: 'mock',
}
