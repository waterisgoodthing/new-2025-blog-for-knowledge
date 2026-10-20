import Link from 'next/link'
import { Home } from 'lucide-react'
import { ThemeToggle } from '@/components/ui-v2'

export function ManageTopbar() {
  return (
    <header className='hidden flex-wrap items-center justify-between gap-3 border-b border-[var(--admin-border)] pb-5 md:flex'>
      <div>
        <p className='text-xs font-medium tracking-[0.18em] text-[var(--brand)]/80'>
          个人学习
        </p>
        <p className='mt-1 text-lg font-semibold text-[var(--admin-text-primary)]'>学习管理空间</p>
      </div>

      <div className='flex items-center gap-2 text-sm'>
        <ThemeToggle />
        <Link
          href='/'
          aria-label='返回公开首页'
          className='inline-flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--admin-surface)]/55 text-[var(--admin-text-secondary)] transition-colors hover:bg-[var(--admin-surface)]/80 hover:text-[var(--admin-text-primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--brand)]/45'
        >
          <Home className='h-4 w-4' aria-hidden='true' />
        </Link>
      </div>
    </header>
  )
}
