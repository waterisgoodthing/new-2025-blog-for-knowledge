import { cn } from '@/lib/utils'

type FormVariant = 'light' | 'heavy'

type ManageFormPanelProps = {
  title?: string
  description?: string
  error?: string
  actions?: React.ReactNode
  variant?: FormVariant
  className?: string
  onSubmit?: React.FormEventHandler<HTMLFormElement>
  children: React.ReactNode
}

const variantStyles: Record<FormVariant, string> = {
  light: 'rounded-lg border border-slate-200/70 bg-white/55 p-5',
  heavy: 'rounded-lg border border-slate-200/70 bg-white/80 p-5 shadow-sm',
}

/**
 * Form layout container for manage pages.
 * Provides unified visual shell: title, description, error, actions.
 * Does not abstract field business, submit logic, or validation —
 * pages own their fields, onSubmit handler, and button state.
 *
 * Visual order: title → children (fields) → error → actions
 * Actions default to right-aligned; use `mr-auto` on a leading button
 * to achieve justify-between within the default flex row.
 */
export function ManageFormPanel({
  title,
  description,
  error,
  actions,
  variant = 'light',
  className,
  onSubmit,
  children,
}: ManageFormPanelProps) {
  return (
    <form
      onSubmit={onSubmit}
      className={cn('space-y-4', variantStyles[variant], className)}
    >
      {(title || description) && (
        <div>
          {title && (
            <h2 className='font-medium text-slate-800'>{title}</h2>
          )}
          {description && (
            <p className='mt-1 text-sm text-slate-500'>{description}</p>
          )}
        </div>
      )}
      {children}
      {error && (
        <p role='alert' className='text-sm text-red-600'>
          {error}
        </p>
      )}
      {actions && (
        <div className='flex flex-wrap items-center justify-end gap-3 pt-2'>
          {actions}
        </div>
      )}
    </form>
  )
}
