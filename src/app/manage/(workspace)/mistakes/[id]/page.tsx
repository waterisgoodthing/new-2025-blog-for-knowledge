import { MistakeDetail } from '../components/mistake-detail'

export default async function ManageMistakeDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>
  searchParams: Promise<{ kind?: string }>
}) {
  const [{ id }, query] = await Promise.all([params, searchParams])
  return <MistakeDetail id={id} kind={query.kind === 'draft' ? 'draft' : 'mistake'} />
}
