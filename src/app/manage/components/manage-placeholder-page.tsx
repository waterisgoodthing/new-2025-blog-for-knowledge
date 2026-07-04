import { Clock3 } from 'lucide-react'
import { ManagePageHeader } from './manage-page-header'

interface ManagePlaceholderPageProps {
  batch: string
  title: string
  description: string
  futureScope: string
}

export function ManagePlaceholderPage({
  batch,
  title,
  description,
  futureScope,
}: ManagePlaceholderPageProps) {
  return (
    <div className='space-y-10'>
      <ManagePageHeader eyebrow={batch} title={title} description={description} />

      <section
        aria-label={`${title}启用状态`}
        className='border-t border-white/55 pt-7'
      >
        <div className='flex max-w-2xl items-start gap-3'>
          <span className='mt-0.5 inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[var(--color-brand)]/10 text-[var(--color-brand)]'>
            <Clock3 className='h-4 w-4' aria-hidden='true' />
          </span>
          <div>
            <h2 className='font-medium text-slate-800'>后续批次启用</h2>
            <p className='mt-1 text-sm leading-6 text-slate-500'>{futureScope}</p>
          </div>
        </div>
      </section>
    </div>
  )
}
