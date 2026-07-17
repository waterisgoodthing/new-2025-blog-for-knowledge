import { cn } from '@/lib/utils'

type EmptyStateVariant = 'loading' | 'empty' | 'filtered-empty' | 'error'

type ManageEmptyStateProps = {
  variant: EmptyStateVariant
  message: string
  action?: React.ReactNode
  className?: string
}

const variantStyles: Record<EmptyStateVariant, string> = {
  loading: 'text-slate-400',
  empty: 'text-slate-500',
  'filtered-empty': 'text-slate-500',
  error: 'text-red-600',
}

/**
 * Compact state placeholder for manage lists and panels.
 * Keeps container dimensions stable — does not expand to fill the page.
 */
export function ManageEmptyState({
  variant,
  message,
  action,
  className,
}: ManageEmptyStateProps) {
  return (
    <div
      className={cn('py-6 text-sm', variantStyles[variant], className)}
      role={variant === 'error' ? 'alert' : variant === 'loading' ? 'status' : undefined}
    >
      <p>{message}</p>
      {action && <div className='mt-2'>{action}</div>}
    </div>
  )
}
