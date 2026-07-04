import { ManagePageHeader } from '../../components/manage-page-header'
import { ReviewQueue } from './review-queue'

export default function ManageReviewPage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='Batch 4 · 固定间隔复习'
        title='复习'
        description='展示已到期的私有错题复习项，并用 0 到 5 分记录一次人工复习。'
      />
      <ReviewQueue />
    </div>
  )
}
