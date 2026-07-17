import { ManagePlaceholderPage } from '../../../components/manage-placeholder-page'

export default function DraftDetailPage() {
  return (
    <ManagePlaceholderPage
      batch='Batch 1 Shell'
      title='Draft Detail'
      description='Static detail route container only.'
      futureScope='Draft editing and confirmation belong to later batches. No draft API is called in Batch 1.'
    />
  )
}
