import { FeatureState } from './feature-state'
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

      <section aria-label={`${title}启用状态`}>
        <FeatureState state={{ kind: 'deferred', title: '当前版本未启用', description: futureScope }} />
      </section>
    </div>
  )
}
