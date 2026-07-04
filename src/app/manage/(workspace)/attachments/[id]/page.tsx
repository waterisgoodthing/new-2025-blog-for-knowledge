import { AttachmentDetail } from '../components/attachment-detail'

export default async function ManageAttachmentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return <AttachmentDetail id={id} />
}
