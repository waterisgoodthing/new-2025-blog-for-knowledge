import { ManagePlaceholderPage } from '../../components/manage-placeholder-page'

export default function ManageSearchPage() {
  return (
    <ManagePlaceholderPage
      batch='Batch 1 Shell'
      title='Search'
      description='Static page container for future admin search.'
      futureScope='Search indexing, filters, and private-result queries are not part of Batch 1. No search API is called here.'
    />
  )
}
