'use client'

import { Uiv2ReviewSection, useReviewQueueModel } from '@/features/ui-v2/review'

export default function ManageReviewPage() {
	const { model, refresh } = useReviewQueueModel()
	return <Uiv2ReviewSection model={model} onRetry={refresh} />
}
