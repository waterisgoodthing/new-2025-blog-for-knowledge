import { cn } from '@/lib/utils'

type PanelVariant = 'light' | 'heavy'

type ManagePanelProps = {
  title?: string
  description?: string
  actions?: React.ReactNode
  variant?: PanelVariant
  className?: string
  children: React.ReactNode
}

const variantStyles: Record<PanelVariant, string> = {
  light: 'rounded-lg border border-slate-200/70 bg-white/55 p-5',
  heavy: 'rounded-lg border border-slate-200/70 bg-white/80 p-5 shadow-sm',
}

/**
 * Lightweight content panel for manage pages.
 * Handles border, background, padding, and optional header area only.
 * Does not encapsulate API, DTO, or business logic.
 */
export function ManagePanel({
  title,
  description,
  actions,
  variant = 'light',
  className,
  children,
}: ManagePanelProps) {
  return (
    <div className={cn(variantStyles[variant], className)}>
      {(title || actions) && (
        <div className='mb-4 flex flex-wrap items-center justify-between gap-3'>
          <div>
            {title && (
              <h2 className='font-semibold text-slate-900'>{title}</h2>
            )}
            {description && (
              <p className='mt-0.5 text-sm text-slate-500'>{description}</p>
            )}
          </div>
          {actions && <div className='flex items-center gap-2'>{actions}</div>}
        </div>
      )}
      {children}
    </div>
  )
}
