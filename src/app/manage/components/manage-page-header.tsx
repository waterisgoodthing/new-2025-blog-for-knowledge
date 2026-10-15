interface ManagePageHeaderProps {
  eyebrow?: string
  title: string
  description: string
}

export function ManagePageHeader({
  eyebrow = '学习工作区',
  title,
  description,
}: ManagePageHeaderProps) {
  return (
    <div className='max-w-2xl'>
      <p className='text-xs font-medium tracking-[0.16em] text-[var(--color-brand)]/75 uppercase'>
        {eyebrow}
      </p>
      <h1 className='mt-2 text-3xl font-semibold tracking-tight text-slate-900 md:text-4xl'>
        {title}
      </h1>
      <p className='mt-3 text-sm leading-6 text-slate-500 md:text-base'>{description}</p>
    </div>
  )
}
