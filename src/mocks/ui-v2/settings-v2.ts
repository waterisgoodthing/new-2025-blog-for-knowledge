import type { LearningSettings } from '../../contracts/ui-v2/settings'
import type { UiPageModel } from '../../contracts/ui-v2/ui-state'

// Settings mocks (U11): display preferences only. No auth content anywhere.

const normal: LearningSettings = {
	dailyReviewGoal: 10,
	density: 'comfortable',
	showMasteryDetails: true,
	source: 'mock',
}

export const mockSettingsNormal: UiPageModel<LearningSettings> = {
	state: 'ready',
	data: normal,
	error: null,
	source: 'mock',
}

export const mockSettingsLoading: UiPageModel<LearningSettings> = {
	state: 'loading',
	data: null,
	error: null,
	source: 'mock',
}

export const mockSettingsError: UiPageModel<LearningSettings> = {
	state: 'error',
	data: null,
	error: 'mock: 学习设置加载失败，请重试',
	source: 'mock',
}
