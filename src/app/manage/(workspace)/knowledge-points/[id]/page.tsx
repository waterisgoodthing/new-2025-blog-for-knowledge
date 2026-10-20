import { KnowledgePointEditor } from '../../subjects/components/knowledge-point-editor'

export default async function KnowledgePointDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return <KnowledgePointEditor knowledgePointId={Number(id)} />
}
