import { ManagePlaceholderPage } from '../../components/manage-placeholder-page'

export default function ManageDraftsPage() {
  return (
    <ManagePlaceholderPage
      batch='Batch 1 Shell'
      title='Drafts'
      description='Static page container for future review queues.'
      futureScope='Question drafts, mistake drafts, and human review workflows are deferred to later batches. No draft API is called in Batch 1.'
    />
  )
}
