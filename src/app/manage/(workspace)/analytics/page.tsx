import { ManagePlaceholderPage } from '../../components/manage-placeholder-page'

export default function ManageAnalyticsPage() {
  return (
    <ManagePlaceholderPage
      batch='后续能力'
      title='学习分析'
      description='当前版本未启用学习指标与趋势分析。'
      futureScope='本页面不计算指标、不展示模拟图表，也不创建 Learning Analytics 数据表。'
    />
  )
}
