import { Ban, Clock3 } from 'lucide-react'

import { ManagePageHeader } from '../../components/manage-page-header'

interface FutureCapabilitySection {
  title: string
  description: string
  items: string[]
}

interface FutureCapabilityPageProps {
  eyebrow: string
  title: string
  description: string
  sections: FutureCapabilitySection[]
  disabledActions: string[]
}

export function FutureCapabilityPage({
  eyebrow,
  title,
  description,
  sections,
  disabledActions,
}: FutureCapabilityPageProps) {
  return (
    <div className='space-y-8'>
      <ManagePageHeader eyebrow={eyebrow} title={title} description={description} />

      <section className='rounded-3xl border border-amber-200/70 bg-amber-50/70 p-5'>
        <div className='flex gap-3'>
          <span className='mt-0.5 inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-amber-100 text-amber-700'>
            <Ban className='h-4 w-4' aria-hidden='true' />
          </span>
          <div>
            <h2 className='font-semibold text-amber-900'>还没有这个功能</h2>
            <p className='mt-1 text-sm leading-6 text-amber-800'>
              这个功能还在准备中，暂时不能使用。
            </p>
          </div>
        </div>
      </section>

      <div className='grid gap-5 lg:grid-cols-3'>
        {sections.map((section) => (
          <section key={section.title} className='rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-sm'>
            <div className='flex items-center gap-2'>
              <Clock3 className='h-4 w-4 text-[var(--color-brand)]' aria-hidden='true' />
              <h2 className='font-semibold text-slate-900'>{section.title}</h2>
            </div>
            <p className='mt-2 text-sm leading-6 text-slate-500'>{section.description}</p>
            <ul className='mt-4 space-y-2 text-sm text-slate-600'>
              {section.items.map((item) => (
                <li key={item} className='rounded-2xl bg-slate-50 px-3 py-2'>
                  {item}
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>

      <section className='rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-sm'>
        <h2 className='font-semibold text-slate-900'>本批明确不提供的操作</h2>
        <div className='mt-4 flex flex-wrap gap-2'>
          {disabledActions.map((action) => (
            <span key={action} className='rounded-full bg-slate-100 px-3 py-1.5 text-sm text-slate-500'>
              {action}
            </span>
          ))}
        </div>
      </section>
    </div>
  )
}
