import { Uiv2PageHeader } from '@/components/ui-v2'
import { DraftWorkspace } from './components/draft-workspace'

export default function ManageDraftsPage() {
  return (
    <div className='space-y-8'>
      <Uiv2PageHeader
        eyebrow='内容管理'
        title='草稿'
        subtitle='确认题目与错题草稿后，再将内容纳入正式学习流程。'
      />
      <DraftWorkspace />
    </div>
  )
}
