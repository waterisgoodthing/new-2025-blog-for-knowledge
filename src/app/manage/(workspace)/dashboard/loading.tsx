import { AsyncStatePanel } from '@/components/async-state-panel'

export default function DashboardLoading() {
  return <AsyncStatePanel status='loading' loadingLabel='正在加载学习概览' skeletonRows={5} />
}
