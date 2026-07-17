import Link from 'next/link'

import { cn } from '@/lib/utils'

type ManageTableContainerProps = {
  header?: React.ReactNode
  count?: number
  countLabel?: string
  className?: string
  children: React.ReactNode
}

/**
 * Composable list/table shell for manage pages.
 * Provides unified list header, count badge, and container styling.
 * Rows and their content are rendered by the parent — this is not
 * a columns/data/filters framework.
 */
export function ManageTableContainer({
  header,
  count,
  countLabel = '条',
  className,
  children,
}: ManageTableContainerProps) {
  return (
    <div className={cn('', className)}>
      {header && (
        <div className='flex items-center justify-between gap-4 border-b border-slate-200/70 pb-3'>
          {header}
          {typeof count === 'number' && (
            <span className='text-xs text-slate-400'>
              {count} {countLabel}
            </span>
          )}
        </div>
      )}
      {children}
    </div>
  )
}

type ManageListRowProps = {
  href: string
  title: string
  meta?: string
  className?: string
  children?: React.ReactNode
}

/**
 * Standard list row for manage pages — link-based, not table-row-based.
 * Matches the existing row pattern across all manage workspaces.
 */
export function ManageListRow({
  href,
  title,
  meta,
  className,
  children,
}: ManageListRowProps) {
  return (
    <Link
      href={href}
      className={cn(
        'group flex items-center gap-4 border-b border-slate-200/55 py-4 transition-colors hover:bg-white/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45',
        className,
      )}
    >
      <span className='min-w-0 flex-1'>
        <span className='block truncate font-medium text-slate-800'>{title}</span>
        {meta && (
          <span className='mt-0.5 block truncate text-xs text-slate-400'>{meta}</span>
        )}
      </span>
      {children}
    </Link>
  )
}
