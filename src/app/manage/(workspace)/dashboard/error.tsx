'use client'

import { AsyncStatePanel } from '@/components/async-state-panel'

export default function DashboardError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <AsyncStatePanel status='error' title='学习管理首页加载失败' error={error} onRetry={reset} />
}
