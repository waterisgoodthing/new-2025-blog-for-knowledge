import { Uiv2PageHeader } from '@/components/ui-v2'
import { ReviewQueue } from './review-queue'

export default function ManageReviewPage() {
  return (
    <div className='space-y-8'>
      <Uiv2PageHeader
        eyebrow='学习计划'
        title='复习'
        subtitle='处理已确认错题的到期复习与不可变复习记录。'
      />
      <ReviewQueue />
    </div>
  )
}
