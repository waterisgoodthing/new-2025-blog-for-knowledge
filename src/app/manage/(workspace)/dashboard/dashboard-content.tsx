'use client'

import useSWR from 'swr'

import { getAdminProfile } from '@/lib/api/admin-profile'
import { getDashboardSummary } from '@/lib/api/dashboard'
import { FeatureState } from '../../components/feature-state'
import { DashboardOverview } from './dashboard-overview'

export function DashboardContent() {
  const { data, error, isLoading, mutate } = useSWR(
    'manage-dashboard-summary',
    getDashboardSummary,
    { revalidateOnFocus: false },
  )
  const profileState = useSWR('manage-admin-profile', getAdminProfile, { revalidateOnFocus: false })

  if (isLoading) {
    return <FeatureState state={{ kind: 'loading', label: '正在加载学习概览', rows: 5 }} />
  }

  if (error || !data) {
    return <FeatureState state={{ kind: 'error', title: '学习概览加载失败', description: '请检查服务状态后重试。', retry: () => void mutate() }} />
  }

  return <DashboardOverview summary={data} profile={profileState.data} profileUnavailable={Boolean(profileState.error)} onProfileRetry={() => void profileState.mutate()} />
}
