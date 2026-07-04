import { ManagePageHeader } from '../../components/manage-page-header'
import { AttachmentWorkspace } from './components/attachment-workspace'

export default function ManageAttachmentsPage() {
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='Batch 5 · 私有附件'
        title='附件'
        description='上传和查看私有学习材料，后续通过 attachment links 关联草稿、题目和错题。'
      />
      <AttachmentWorkspace />
    </div>
  )
}
