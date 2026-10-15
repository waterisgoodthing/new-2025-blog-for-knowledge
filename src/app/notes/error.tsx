'use client'

import { AsyncStatePanel } from '@/components/async-state-panel'

export default function NotesError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <AsyncStatePanel status='error' title='笔记页面加载失败' error={error} onRetry={reset} />
}
