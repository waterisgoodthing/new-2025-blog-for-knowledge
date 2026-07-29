import { ManagePageHeader } from '../../../components/manage-page-header'
import { DraftEditor } from '../components/draft-editor'

export default async function DraftDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='内容管理'
        title='草稿详情'
        description='人工校对草稿后，可确认进入正式题库。'
      />
      <DraftEditor draftId={id} />
    </div>
  )
}
