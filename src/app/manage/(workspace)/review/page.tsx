import { ManagePageHeader } from '../../components/manage-page-header'
import { ReviewQueue } from './review-queue'

export default function ManageReviewPage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='学习计划'
        title='复习'
        description='处理已确认错题的到期复习与不可变复习记录。'
      />
      <ReviewQueue />
    </div>
  )
}
