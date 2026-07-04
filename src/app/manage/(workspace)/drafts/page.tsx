import { ManagePageHeader } from '../../components/manage-page-header'
import { DraftWorkspace } from './components/draft-workspace'

export default function ManageDraftsPage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='Batch 3 · 人工审核'
        title='题目草稿'
        description='所有手工题目先在这里修正并确认，再进入正式题库。'
      />
      <DraftWorkspace />
    </div>
  )
}
