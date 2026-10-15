import { SubjectEditor } from '../components/subject-editor'

export default async function SubjectDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return <SubjectEditor subjectId={Number(id)} />
}
