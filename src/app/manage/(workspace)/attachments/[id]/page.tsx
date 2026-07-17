import { ManagePageHeader } from '../../../components/manage-page-header'
import { AttachmentDetail } from '../components/attachment-detail'

export default async function ManageAttachmentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='Private Workspace'
        title='Attachment Detail'
        description='查看私有附件、内容预览与学习对象关联。'
      />
      <AttachmentDetail id={id} />
    </div>
  )
}
