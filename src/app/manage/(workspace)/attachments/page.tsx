import { Uiv2PageHeader } from '@/components/ui-v2'
import { AttachmentWorkspace } from './components/attachment-workspace'

export default function ManageAttachmentsPage() {
  return (
    <div className='space-y-7'>
      <Uiv2PageHeader eyebrow='资料管理' title='附件' subtitle='管理私有学习附件及其题目、草稿、错题关联。' />
      <AttachmentWorkspace />
    </div>
  )
}
