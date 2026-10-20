import { Uiv2PageHeader } from '@/components/ui-v2'
import { AttachmentDetail } from '../components/attachment-detail'

export default async function ManageAttachmentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return (
    <div className='space-y-8'>
      <Uiv2PageHeader eyebrow='资料管理' title='附件详情' subtitle='查看私有附件、内容预览与学习对象关联。' />
      <AttachmentDetail id={id} />
    </div>
  )
}
