import { ManagePageHeader } from '../../../components/manage-page-header'
import { MistakeDetail } from '../components/mistake-detail'

export default async function ManageMistakeDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>
  searchParams: Promise<{ kind?: string }>
}) {
  const { id } = await params
  const { kind } = await searchParams
  const detailKind = kind === 'draft' ? 'draft' : 'mistake'
  return (
    <div className='space-y-8'>
      <ManagePageHeader
        eyebrow='内容管理'
        title={detailKind === 'draft' ? '错题草稿' : '错题详情'}
        description={detailKind === 'draft' ? '人工确认错题草稿后，才会进入正式错题与复习。' : '查看和维护已确认的私有错题。'}
      />
      <MistakeDetail id={id} kind={detailKind} />
    </div>
  )
}
