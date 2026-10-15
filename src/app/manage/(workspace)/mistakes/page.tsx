'use client'

import { useState } from 'react'

import type { MistakeFilterModel } from '@/contracts/ui-v2/mistake'
import { Uiv2MistakesSection, useMistakesModel } from '@/features/ui-v2/mistakes'

const DEFAULT_FILTER: MistakeFilterModel = {
	status: 'all',
	reason: 'all',
	knowledgePointId: null,
	query: '',
}

export default function ManageMistakesPage() {
	const { model, refresh } = useMistakesModel()
	const [filter, setFilter] = useState<MistakeFilterModel>(DEFAULT_FILTER)
	return (
		<Uiv2MistakesSection
			model={model}
			filter={filter}
			onFilterChange={setFilter}
			onRetry={refresh}
		/>
	)
}
