import { CircleAlert, Clock3, Inbox } from 'lucide-react'

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
    const rows = Math.max(1, state.rows ?? 4)
    const label = state.label ?? '正在加载内容'
    return (
      <div role='status' aria-label={label} className='space-y-3 py-4'>
        <span className='sr-only'>{label}</span>
        {Array.from({ length: rows }, (_, index) => (
          <div
            key={index}
            data-testid='feature-state-skeleton'
            className='animate-pulse border-b border-slate-200/55 pb-3'
            aria-hidden='true'
          >
            <div className='h-3 w-2/5 rounded-full bg-slate-200/75' />
            <div className='mt-2 h-2.5 w-3/5 rounded-full bg-slate-100' />
          </div>
        ))}
      </div>
    )
  }

  const isDeferred = state.kind === 'deferred'
  const isError = state.kind === 'error'
  const Icon = isDeferred ? Clock3 : isError ? CircleAlert : Inbox

  return (
    <div className='flex min-h-44 items-center border-y border-slate-200/60 py-8'>
      <div className='max-w-lg'>
        {isDeferred ? (
          <p className='mb-2 text-xs font-medium tracking-[0.12em] text-amber-700 uppercase'>后续能力</p>
        ) : null}
        <div className='flex items-start gap-3'>
          <span className={`mt-0.5 inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${isError ? 'bg-red-50 text-red-600' : isDeferred ? 'bg-amber-50 text-amber-700' : 'bg-slate-100 text-slate-500'}`}>
            <Icon className='h-4 w-4' aria-hidden='true' />
          </span>
          <div>
            <h2 className='font-semibold text-slate-900'>{state.title}</h2>
            {state.description ? (
              <p className='mt-1 text-sm leading-6 text-slate-500'>{state.description}</p>
            ) : null}
            {state.kind === 'empty' && state.action ? (
              <button
                type='button'
                onClick={state.action.onClick}
                className='mt-4 rounded-lg bg-[var(--color-brand)] px-4 py-2 text-sm font-medium text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'
              >
                {state.action.label}
              </button>
            ) : null}
            {state.kind === 'error' && state.retry ? (
              <button
                type='button'
                onClick={state.retry}
                className='mt-4 rounded-lg border border-slate-200 bg-white/70 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'
              >
                重新尝试
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}
