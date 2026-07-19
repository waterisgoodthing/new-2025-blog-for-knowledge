import { ManagePlaceholderPage } from '../../components/manage-placeholder-page'

export default function ManageSearchPage() {
  return (
    <ManagePlaceholderPage
      batch='后续能力'
      title='搜索'
      description='当前版本未启用跨内容搜索。'
      futureScope='本页面不建立索引、不查询私有内容，也不显示模拟搜索结果。'
    />
  )
}
