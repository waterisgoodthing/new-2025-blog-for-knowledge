import Link from 'next/link'
import { Home } from 'lucide-react'

export function ManageTopbar() {
  return (
    <header className='hidden flex-wrap items-center justify-between gap-3 border-b border-white/45 pb-5 md:flex'>
      <div>
        <p className='text-xs font-medium tracking-[0.18em] text-[var(--color-brand)]/80 uppercase'>
          Personal learning
        </p>
        <p className='mt-1 text-lg font-semibold text-slate-800'>学习管理空间</p>
      </div>

      <div className='flex items-center gap-2 text-sm'>
        <Link
          href='/'
          aria-label='返回公开首页'
          className='inline-flex h-9 w-9 items-center justify-center rounded-lg bg-white/55 text-slate-500 transition-colors hover:bg-white/80 hover:text-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-brand)]/45'
        >
          <Home className='h-4 w-4' aria-hidden='true' />
        </Link>
      </div>
    </header>
  )
}
