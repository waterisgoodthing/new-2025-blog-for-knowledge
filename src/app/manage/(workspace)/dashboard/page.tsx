'use client'

import { Uiv2DashboardSection, useDashboardModel } from '@/features/ui-v2/dashboard'

export default function ManageDashboardPage() {
	const { model, refresh } = useDashboardModel()
	return <Uiv2DashboardSection model={model} onRetry={refresh} />
}
