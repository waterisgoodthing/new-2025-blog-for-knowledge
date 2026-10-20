import { Clock3 } from 'lucide-react'

import { AsyncStatePanel } from '@/components/async-state-panel'

export type FeatureStateModel =
  | { kind: 'loading'; label?: string; rows?: number }
  | {
      kind: 'empty'
      title: string
      description?: string
      action?: { label: string; onClick: () => void }
    }
  | {
      kind: 'error'
      title: string
      description?: string
      retry?: () => void
    }
  | { kind: 'deferred'; title: string; description: string }

type FeatureStateProps = {
  state: FeatureStateModel
}

export function FeatureState({ state }: FeatureStateProps) {
  if (state.kind === 'loading') {
    return <AsyncStatePanel status='loading' loadingLabel={state.label} skeletonRows={state.rows} skeletonTestId='feature-state-skeleton' />
  }

  const isDeferred = state.kind === 'deferred'
  if (isDeferred) {
    return (
      <div className='flex min-h-44 items-center border-y border-[var(--admin-border)]/60 py-8'>
        <div className='max-w-lg'>
          <p className='mb-2 text-xs font-medium tracking-[0.12em] text-amber-700 uppercase'>后续能力</p>
          <div className='flex items-start gap-3'>
            <span className='mt-0.5 inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-amber-50 text-amber-700'>
              <Clock3 className='h-4 w-4' aria-hidden='true' />
            </span>
            <div>
              <h2 className='font-semibold text-[var(--admin-text-primary)]'>{state.title}</h2>
              <p className='mt-1 text-sm leading-6 text-[var(--admin-text-secondary)]'>{state.description}</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (state.kind === 'empty') {
    return <AsyncStatePanel status='empty' title={state.title} emptyHint={<>{state.description ? <p>{state.description}</p> : null}{state.action ? <button type='button' onClick={state.action.onClick} className='mt-4 rounded-lg bg-[var(--brand)] px-4 py-2 text-sm font-medium text-white'>{state.action.label}</button> : null}</>} />
  }

  return <AsyncStatePanel status='error' title={state.title} error={state.description} onRetry={state.retry} retryLabel='重新尝试' />
}
