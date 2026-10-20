import { cn } from '@/lib/utils'

type Tone = 'neutral' | 'info' | 'success' | 'warning' | 'danger'

type StatusBadgeProps = {
  tone: Tone
  children: React.ReactNode
  className?: string
}

const toneStyles: Record<Tone, string> = {
  neutral: 'bg-slate-100 text-slate-600',
  info: 'bg-blue-50 text-blue-700',
  success: 'bg-emerald-50 text-emerald-700',
  warning: 'bg-amber-50 text-amber-700',
  danger: 'bg-red-50 text-red-700',
}

/**
 * Semantic status badge for manage pages.
 * Pages must explicitly map domain status to tone — this component
 * does not interpret business enum values.
 */
export function ManageStatusBadge({ tone, children, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        toneStyles[tone],
        className,
      )}
    >
      {children}
    </span>
  )
}
