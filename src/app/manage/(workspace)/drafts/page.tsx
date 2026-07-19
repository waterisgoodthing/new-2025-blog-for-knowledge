import { ManagePageHeader } from '../../components/manage-page-header'
import { DraftWorkspace } from './components/draft-workspace'

export default function ManageDraftsPage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='内容管理'
        title='草稿'
        description='确认题目与错题草稿后，再将内容纳入正式学习流程。'
      />
      <DraftWorkspace />
    </div>
  )
}
