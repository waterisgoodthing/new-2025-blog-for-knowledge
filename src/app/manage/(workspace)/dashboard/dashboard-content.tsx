'use client'

import { useEffect, useRef } from 'react'
import useSWR from 'swr'

import { getAdminProfile } from '@/lib/api/admin-profile'
import { getDashboardSummary } from '@/lib/api/dashboard'
import { AsyncStatePanel } from '@/components/async-state-panel'
import { DashboardOverview } from './dashboard-overview'

export function DashboardContent() {
	const resultRegionRef = useRef<HTMLDivElement>(null)
	const retryRequestedRef = useRef(false)
  const { data, error, isLoading, mutate } = useSWR(
    'manage-dashboard-summary',
    getDashboardSummary,
    { revalidateOnFocus: false },
  )
  const profileState = useSWR('manage-admin-profile', getAdminProfile, { revalidateOnFocus: false })

	useEffect(() => {
		if (!data || !retryRequestedRef.current) return
		retryRequestedRef.current = false
		resultRegionRef.current?.focus()
	}, [data])

	const retrySummary = () => {
		retryRequestedRef.current = true
		return mutate()
	}

  if (isLoading) {
    return <AsyncStatePanel status='loading' loadingLabel='正在加载学习概览' skeletonRows={5} skeletonTestId='feature-state-skeleton' />
  }

  if (error || !data) {
    return <AsyncStatePanel status='error' title='学习概览加载失败' error='请检查服务状态后重试。' onRetry={retrySummary} retryLabel='重新尝试' />
  }

	return <div ref={resultRegionRef} role='region' aria-label='学习概览结果' tabIndex={-1} className='outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'><DashboardOverview summary={data} profile={profileState.data} profileError={profileState.error} profileLoading={profileState.isLoading} onProfileRetry={profileState.mutate} onSummaryRetry={retrySummary} /></div>
}
